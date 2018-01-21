# ----------- Script by ReedRGale ----------- #
# Utility functions that lubricate the process of... a lot of things. #


# Import #

import json
import os
import discord
import math
import asyncio
import shlex

from view.TidyMessage import TidyMessage
from asyncio import tasks
from multiprocessing.pool import ThreadPool
from model import st, alias, val
from model.enums import UserType, TidyMode
from controller import calc


# Command Encapsulations #


async def escape_setter(ctx):
    """A function that encapsulates everything regarding changing a personal escape value."""
    # Request new escape value.
    tm = await TidyMessage.build(ctx, get_escape(ctx), st.ESCAPE, content=st.REQ_NEW_ESCAPE,
                                 checks=[check_args_f(st.MODE_EQ, 1)])
    if tm.prompt.content == get_escape(ctx):
        return get_escape(ctx)

    set_escape(ctx, tm.prompt.content)
    await tm.rebuild(st.INF_ESCAPE_SET.format(tm.prompt.content) + " " + st.rand_slack())


async def new_canon(ctx):
    """Makes a canon folder and files."""
    # Ask for RP name
    tm = await TidyMessage.build(ctx, get_escape(ctx), st.ESCAPE, content=st.REQ_NEW_CANON,
                                 checks=[check_args_f(st.MODE_EQ, 1)])
    if tm.prompt.content == get_escape(ctx):
        return get_escape(ctx)
    canon = tm.prompt.content.replace(" ", "_")

    # Path syntactical candy.
    g = str(ctx.guild.id)

    # Check if an RP with this name existed in the past.
    is_archived = None
    if os.path.exists(st.ARCHIVES_P.format(g)):
        archived = os.listdir(st.ARCHIVES_P.format(g))
        for old in archived:
            if old.lower() == canon.lower():
                is_archived = True
                break

    # If it's archived tell them they can revive the RP, or cancel the command.
    if is_archived:
        tm = await tm.rebuild(st.ASK_REVIVE_RP, checks=[check_alias_f(alias.CONFIRM_ALIASES),
                                                        check_args_f(st.MODE_EQ, 1)])
        if tm.prompt.content == get_escape(ctx):
            return get_escape(ctx)
        if tm.prompt.content.lower() in alias.DENY:
            return await tm.rebuild(st.INF_REVIVE_ABORT + " " + st.rand_slack(), req=False)

    # Ask for GM.
    tm = await tm.rebuild(st.INF_REVIVE_A_GO + st.REQ_USER_GM if is_archived else st.REQ_USER_GM,
                          checks=[check_member_f(ctx),
                                  check_args_f(st.MODE_EQ, 1)])
    if tm.prompt.content == get_escape(ctx):
        return get_escape(ctx)
    gm = tm.prompt.content
    have_gm = gm == ctx.author.mention
    borked = False

    # If the GM isn't the maker of the canon, ask them if they want to take on this hell.
    while not have_gm and not borked:
        # Message the user.
        mem = get_member(ctx, mention=gm)
        if not mem.dm_channel:
            await mem.create_dm()
        dm_tm = await TidyMessage.build(ctx, get_escape(ctx), st.ESCAPE, content=st.ASK_IF_GM,
                                        dest=mem.dm_channel, member=mem,
                                        checks=[check_alias_f(alias.CONFIRM_ALIASES),
                                                check_args_f(st.MODE_EQ, 1)])
        if tm.prompt.content == get_escape(ctx):
            result = alias.DENY[0]
        else:
            result = dm_tm.prompt.content

        if result.lower() in alias.AFFIRM:
            await dm_tm.rebuild(st.YOUR_FUNERAL, req=False)
            have_gm = True
        elif result.lower() in alias.DENY:
            await dm_tm.rebuild(st.INF_NOT_GM, req=False)
            borked = True

    # If GM denied the lofty position, let the caller know.
    if borked:
        return await tm.rebuild(st.INF_DENIED_GM)

    # Make category for the canon to reside in.
    category = await ctx.guild.create_category(canon)

    # Path syntactical candy.
    c = str(category.id)

    # Make folder, initial docs and roles.
    if not os.path.exists(st.CANON_P.format(g, c)):
        # Prepare all directories if not just taking from the archive.
        if not is_archived:
            if not os.path.exists(st.ARCHIVES_P.format(g)):
                os.makedirs(st.ARCHIVES_P.format(g))
            os.makedirs(st.CHARACTERS_P.format(g, c))
            os.makedirs(st.C_LOGS_P.format(g, c))
            os.makedirs(st.META_P.format(g, c))
            os.makedirs(st.C_PLAYER_PREFS_P.format(g, c))

            for mem in ctx.guild.members:
                if not os.path.exists(st.MEM_COMMAND_C_LOGS_P.format(g, c, str(mem.id))):
                    os.makedirs(st.MEM_COMMAND_C_LOGS_P.format(g, c, str(mem.id)))
        else:
            # Move archive data to canon
            os.rename(st.ARCHIVE_P.format(g, canon.title()), st.CANON_P.format(g, c))

        # Make a file to handle the command exceptions
        open(st.EXCEPTIONS_P.format(g, c), 'a').close()
        with open(st.EXCEPTIONS_P.format(g, c), 'w') as fout:
            json.dump({}, fout, indent=1)

        # Make roles to discern who can do what.
        role, r_dat = list(), dict()
        for n in UserType:
            r = await ctx.guild.create_role(name=canon.upper() + " " + str(n).upper())
            role.append(r)
            r_dat[r.name] = r.id

        # Record the role ids for later access.
        role_ids = dict()
        open(st.ROLES_P.format(g, c), 'a').close()
        with open(st.ROLES_P.format(g, c), 'w') as fout:
            for r in role:
                role_type = r.name.split()[1]
                role_ids[role_type] = r.id
            json.dump(role_ids, fout, indent=1)

        # For each member in the channel, make a file and add them to the proper role.
        for mem in ctx.guild.members:
            with open(st.C_PLAYER_PREF_P.format(g, c, str(mem.id)), 'w') as fout:
                if gm == mem.mention:
                    pref = {st.FLD_UTYPE: UserType.GM.value, st.FLD_RCHAR: None}
                    await mem.add_roles(role[2])
                else:
                    pref = {st.FLD_UTYPE: UserType.OBSERVER.value, st.FLD_RCHAR: None}
                    await mem.add_roles(role[0])
                json.dump(pref, fout, indent=1)

        status = st.INF_CANON_MADE
    else:
        status = st.ERR_CANON_EXISTS

    # If this doesn't already exist make channels.
    if status != st.ERR_CANON_EXISTS:
        # Prepare permission levels.
        n = discord.PermissionOverwrite(read_messages=False, send_messages=False)
        r = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        rw = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # Make channels for specific purposes per role.
        ch = st.CHNL_ALL
        ch_dat = dict()

        # All can see the Intro Channel on creation.
        channel = await ctx.guild.create_text_channel(canon + ch[0], category=category,
                                                      overwrites={role[0]: r, role[1]: r, role[2]: rw})
        ch_dat[channel.name] = channel.id

        # IC Channel is open to players and the GM.
        channel = await ctx.guild.create_text_channel(canon + ch[1], category=category,
                                                      overwrites={role[0]: r, role[1]: rw, role[2]: rw})
        ch_dat[channel.name] = channel.id

        # OOC Channel is open to all on creation.
        channel = await ctx.guild.create_text_channel(canon + ch[2], category=category,
                                                      overwrites={role[0]: rw, role[1]: rw, role[2]: rw})
        ch_dat[channel.name] = channel.id

        # Command Room is open only to players and the gm.
        channel = await ctx.guild.create_text_channel(canon + ch[3], category=category,
                                                      overwrites={role[0]: n, role[1]: rw, role[2]: rw})
        ch_dat[channel.name] = channel.id

        # Rules is for posting that which people should follow that the bot doesn't enforce.
        channel = await ctx.guild.create_text_channel(canon + ch[4], category=category,
                                                      overwrites={role[0]: r, role[1]: r, role[2]: rw})
        ch_dat[channel.name] = channel.id

        # Meta is for viewing the meta-rules of the canon only. The GM only affects these indirectly.
        channel = await ctx.guild.create_text_channel(canon + ch[5], category=category,
                                                      overwrites={role[0]: r, role[1]: r, role[2]: r})
        ch_dat[channel.name] = channel.id

        # GM Notes is for the gm's eyes only.
        channel = await ctx.guild.create_text_channel(canon + ch[6], category=category,
                                                      overwrites={role[0]: n, role[1]: n, role[2]: rw})
        ch_dat[channel.name] = channel.id

        # Reading Room is for everyone to read, but never directly touch.
        channel = await ctx.guild.create_text_channel(canon + ch[7], category=category,
                                                      overwrites={role[0]: r, role[1]: r, role[2]: r})
        ch_dat[channel.name] = channel.id

        # Record untouchable instance of data.
        with open(st.IDS_P.format(g, c), 'w') as fout:
            json.dump({st.FLD_CHNL: ch_dat, st.FLD_ROLE: r_dat}, fout, indent=1)

    await tm.rebuild(status + " " + st.rand_slack(), req=False)


async def delete_canon(ctx):
    """Deletes a canon and archives its data in case its remade."""
    # Check if canon exists.
    if not get_canon(ctx):
        return TidyMessage.build(ctx, get_escape(ctx), st.ESCAPE, req=False, content=st.ERR_CANON_NONEXIST,
                                 mode=TidyMode.WARNING)

    # Initialize a tm.
    tm = await TidyMessage.build(ctx, get_escape(ctx), st.ESCAPE, req=False, content=st.INF_MESSAGING_D)

    # Collect all players in canon.
    players = list()

    # Prepare categories.
    yes, no = 1, 0  # Yes starts at one because the caller of the function is presumed to support deletion.

    # Tally up all participants in this canon.
    for mem in ctx.guild.members:
        user = get_user_type(mem, ctx.channel)
        if user == UserType.PLAYER.value or (user == UserType.GM.value and mem != ctx.author):
            players.append(mem)

    # Notify users.
    affirmations, pool = list(), ThreadPool()
    for mem in players:
        if not mem.dm_channel:
            await mem.create_dm()
        affirmations.append(asyncio.ensure_future(wait_for_affirmation(ctx, mem.dm_channel, mem, st.ASK_IF_DELETE)))

    # Await results...
    majority = math.ceil((len(players) + yes) / 2)
    while yes < majority and no < majority:
        done, affirmations = await tasks.wait(affirmations, return_when=asyncio.FIRST_COMPLETED)
        for d in done:
            if d.result().prompt.content.lower() in alias.AFFIRM:
                yes += 1
            elif d.result().prompt.content.lower() in alias.DENY:
                no += 1

    # Process results.
    if majority <= yes:
        # Path syntactical candy.
        g = str(ctx.guild.id)
        c = str(ctx.channel.category_id)

        # Delete categories and roles in list.
        guild_name = ctx.guild.get_channel(ctx.channel.category_id).name
        with open(st.IDS_P.format(g, c), 'r') as fout:
            ids_json, roles = json.load(fout), list()
            for ch in ctx.guild.channels:
                if ch.category_id == ctx.channel.category_id and ids_json[st.FLD_CHNL].get(ch.name):
                    await ch.delete(reason=st.INF_DELETE_CHANNEL)
            for r in ctx.guild.roles:
                if ids_json[st.FLD_ROLE].get(r.name):
                    roles.append(r)
            for r in roles:
                await r.delete(reason=st.INF_DELETE_ROLE)
            for ch in ctx.guild.channels:
                if ch.id == ctx.channel.category_id:
                    await ch.delete()

        # Move canon data to archive
        os.rename(st.CANON_P.format(g, c), st.ARCHIVE_P.format(g, guild_name.title()))

    elif no >= majority and yes >= majority or yes < majority and no < majority:
        tm.rebuild(st.ERR_VOTE_FAILED, mode=TidyMode.WARNING)
    else:
        tm.rebuild(st.INF_DENIED_DELETE)


async def new_combat(ctx):
    """Begins a combat by opening the relevant channels"""
    # Ask for players.
    tm = TidyMessage.build(ctx, get_escape(ctx), st.ESCAPE, content=st.REQ_USER_COMBAT,
                           checks=[check_member_f(ctx),
                                   check_args_f(st.MODE_GTE, 2)])
    if tm.prompt.content == get_escape(ctx):
        return get_escape(ctx)
    players = shlex.split(tm.prompt.content)

    # Notify users.
    affirmations, pool = dict(), ThreadPool(processes=len(players))

    for mem in players:
        if not mem.dm_channel:
            await mem.create_dm()
        affirmations.append(asyncio.ensure_future(wait_for_affirmation(ctx, mem.dm_channel, st.ASK_IF_FIGHT)))

    # Process results...
    accounted_for, borked = [], False
    while affirmations and not borked:
        done, affirmations = await tasks.wait(affirmations, return_when=asyncio.FIRST_COMPLETED)
        for d in done:
            m = d.result.message
            if m.content.lower() in alias.AFFIRM:
                accounted_for.append(m.author.mention)
            elif m.content.lower() in alias.DENY:
                borked = True

    # Make private channels and assign roles to given players/GM.
    for af in accounted_for:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            players[af]: discord.PermissionOverwrite(read_messages=True)
        }
        # Pick up from here...
        # await ctx.guild.create_text_channel("Test_Guild", overwrites=overwrites)
        # await t(players[af].dm_channel, st.INF_CHANNELS_MADE)


# Checks #


def check_dups(*args):
    """A check for duplicate values under normal circumstances."""
    return True if len(args) == len(set(args)) else st.ERR_DUP_ARG


def check_int(*args):
    """Check that tells you if every argument is an integer."""
    for a in args:
        if not calc.is_int(a):
            return st.ERR_NOT_INT
    return True


def check_member_f(ctx):
    """A check-factory that makes a check to see if the arguments are all members of a particular context."""
    def check(*args):
        for mem in args:
            if not get_member(ctx, mention=mem):
                return st.ERR_MEMBER_NONEXIST.format(mem)
        return True
    return check


def check_invalid_f(c_set):
    """A check-factory that makes a check that looks to see if there
    isn't any of a set of characters inside each arg."""
    def check(*args):
        for a in args:
            if contains_any(a, c_set):
                return st.ERR_INV_USER_CONTENT_I.format(c_set)
        return True
    return check


def check_valid_f(c_set):
    """A check-factory that makes a check that looks to see if there's
    any of a set of characters inside each arg."""
    def check(*args):
        for a in args:
            if not is_any(a, c_set):
                return st.ERR_INV_USER_CONTENT_V.format(c_set)
        return True
    return check


def check_args_f(op, num):
    """A check-factory that makes a check that looks at the number of args relative to an operator.
        len(args) <op> num :: Plain English: the number of args should be <op> 'num' otherwise throw an error."""
    if op == st.MODE_GT:
        def check(*args):
            return True if len(args) > num else st.ERR_TOO_FEW_ARGS.format("more than", str(num))
    elif op == st.MODE_GTE:
        def check(*args):
            return True if len(args) >= num else st.ERR_TOO_FEW_ARGS.format(str(num), "or more")
    elif op == st.MODE_LT:
        def check(*args):
            return True if len(args) < num else st.ERR_TOO_MANY_ARGS.format("less than", str(num))
    elif op == st.MODE_LTE:
        def check(*args):
            return True if len(args) <= num else st.ERR_TOO_MANY_ARGS.format(str(num), "or less")
    elif op == st.MODE_EQ:
        def check(*args):
            return True if len(args) == num else st.ERR_INEXACT_ARGS.format(str(num))
    else:  # I hate myself, so fail silently and just not check the args for not inputting things properly.
        def check(*args):
            return True
    return check


def check_alias_f(aliases, no_dups=False):
    """A check-factory that makes a check that looks to see if there's
     any of a set of characters inside of an alias [dictionary of values]."""
    def check(*args):
        # Prepare a list to measure variables already used and another to count checks.
        used, c_list, matched = list(), list(), False

        # Check each alias against each argument.
        for a in args:
            for name in aliases:
                for al in aliases[name]:
                    matched = al.lower() == a.lower()
                    if matched and name in used and no_dups:
                        return st.ERR_REPEAT_VAL.format(a)
                    elif matched:
                        used.append(name)
                        break
                if matched:
                    break
            if not matched:
                return st.ERR_NOT_IN_ALIAS.format(a)
        return True
    return check


# Tasks #


async def wait_for_affirmation(ctx, channel, member, content):
    """Method to encapsulate all parts of asking if someone is joining in a combat."""
    tm = await TidyMessage.build(ctx, get_escape(ctx), st.ESCAPE, content=content, dest=channel, member=member,
                                 checks=[check_alias_f(alias.CONFIRM_ALIASES),
                                         check_args_f(st.MODE_EQ, 1)])
    return await tm.rebuild("Vote tallied.", req=False)


# Utility #


def check_perms(ctx):
    """Provides information about command relative to the member calling the command."""
    # Collect the command name.
    command = ctx.command.full_parent_name.replace(" ", "_") + "_" + ctx.command.name

    if get_canon(ctx) and val.perms[command]:
        # Check role of player against those allowed to call command.
        can_call = get_user_type(ctx.message.author, ctx.channel) in val.perms[command]

        # Path syntactical candy.
        g = str(ctx.guild.id)
        c = str(ctx.channel.category_id)

        # Check if on exception list.
        with open(st.EXCEPTIONS_P.format(g, c), 'r') as fout:
            exc_json = json.load(fout)
            can_call = can_call or (exc_json.get(command).get(ctx.message.author.id)
                                    if exc_json.get(command) else False)

        # If not allowed, then return error.
        if not can_call:
            return st.ERR_INSUF_PERMS

    elif val.perms[command]:
        return st.ERR_NOT_IN_CANON

    elif get_canon(ctx):
        return st.ERR_IN_CANON

    return None


def update_g_player_prefs(guild):
    """Initializes the player prefs if they don't exist."""
    # Make folder and initial docs if they don't exist.
    if not os.path.exists(st.G_PLAYER_PREFS_P.format(str(guild.id))):
        os.makedirs(st.G_PLAYER_PREFS_P.format(str(guild.id)))
    if not os.path.exists(st.COMMAND_G_LOGS_P.format(str(guild.id))):
        os.makedirs(st.COMMAND_G_LOGS_P.format(str(guild.id)))

    # For each member in the channel, make a file.
    for mem in guild.members:
        if not os.path.exists(st.G_PLAYER_PREF_P.format(str(guild.id), str(mem.id))):
            with open(st.G_PLAYER_PREF_P.format(str(guild.id), str(mem.id)), 'a') as fout:
                pref = {st.FLD_ESC: '~'}
                json.dump(pref, fout, indent=1)
        if not os.path.exists(st.MEM_COMMAND_G_LOGS_P.format(str(guild.id), str(mem.id))):
            os.makedirs(st.MEM_COMMAND_G_LOGS_P.format(str(guild.id), str(mem.id)))


def get_prefs(member, channel):
    """Returns the prefs of the user as a JSON."""
    # Path syntactical candy.
    g = str(channel.guild.id)
    c = str(channel.category_id)
    m = str(member.id)
    if os.path.exists(st.C_PLAYER_PREF_P.format(g, c, m)):
        with open(st.C_PLAYER_PREF_P.format(g, c, m), 'r') as fin:
            prefs = json.load(fin)
        return prefs
    return None


def get_canon(ctx):
    """Returns the category file path or None of doesn't exist."""
    if ctx.channel.category_id:
        canon = st.CANON_P.format(str(ctx.guild.id), str(ctx.channel.category_id))
        return canon if os.path.exists(canon) else None


def get_user_type(member, channel):
    """Returns the usertype of a member relative to the channel being called from."""
    return get_prefs(member, channel).get(st.FLD_UTYPE)


def get_character_json(character, channel):
    """Returns an dictionary of character stats."""
    # Path syntactical candy.
    g = str(channel.guild.id)
    c = str(channel.category_id)

    # Pull JSON file for reading.
    open(st.CHARACTER_P.format(g, c, character), 'a').close()
    with open(st.CHARACTER_P.format(g, c, character), 'r') as fin:
        if os.stat(st.CHARACTER_P.format(g, c, character)).st_size > 0:
            a = json.load(fin)
        else:
            a = {}
    return a


def get_member(ctx, mention):
    """Returns the user by mention or None, if none found."""
    # Link members to their mentions.
    members = {}
    for mem in ctx.guild.members:
        members[mem.mention] = mem

    return members.get(mention)


def get_escape(ctx):
    """Get the escape value of a member."""
    # Path syntactical candy.
    g = str(ctx.guild.id)
    a = str(ctx.author.id)
    with open(st.G_PLAYER_PREF_P.format(g, a), 'r') as fin:
        pref_json = json.load(fin)
    return pref_json[st.FLD_ESC]


def get_app_token():
    with open('token.txt', 'r') as token:
        token = token.read()
    return token


def redeem_alias(alias_i, aliases):
    """Returns the normalized form (first element in the list) of an alias value"""
    # Compare alias to other aliases
    for a in aliases:
        for value in aliases[a]:
            if value.lower() == alias_i.lower():
                return aliases[a][0]
    return None


def set_escape(ctx, escape):
    """Set the escape value of a member."""
    # Path syntactical candy.
    g = str(ctx.guild.id)
    a = str(ctx.author.id)

    # Get the current prefs.
    with open(st.G_PLAYER_PREF_P.format(g, a), 'r') as fin:
        pref_json = json.load(fin)

    # Load and dump the new prefs with the changed escape.
    pref_json[st.FLD_ESC] = escape
    with open(st.G_PLAYER_PREF_P.format(g, a), 'w') as fout:
        json.dump(pref_json, fout, indent=1)


def contains_any(content, chars):
    for c in chars:
        if c in content:
            return True
    return False


def is_any(content, vals):
    for v in vals:
        if v.lower() == content.lower():
            return True
    return False