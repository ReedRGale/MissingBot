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


# TODO: Test
async def escape_setter(ctx):
    """A function that encapsulates everything regarding changing a personal escape value."""
    # Request new escape value.
    tm = await TidyMessage.build(ctx, get_escape(ctx), content=st.REQ_NEW_CANON,
                                 checks=[check_args_f("==", 1)])
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)

    set_escape(ctx, tm.message.content)
    tm.rebuild(st.INF_ESCAPE_SET.format(tm.message.content))


# TODO: Test
async def make_canon(ctx):
    """Makes a canon folder and files."""
    # Ask for RP name
    tm = await TidyMessage.build(ctx, get_escape(ctx), content=st.REQ_NEW_CANON,
                                 checks=[check_args_f("==", 1)])
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)
    canon = tm.message.content

    canon = canon[0].replace(" ", "_")

    # Ask for GM.
    tm = tm.rebuild(st.REQ_USER_GM,
                    checks=[check_member_f(ctx),
                            check_args_f("==", 1)])
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)
    gm = tm.message.content
    have_gm = gm == ctx.author.mention
    borked = False

    # If the GM isn't the maker of the canon, ask them if they want to take on this hell.
    while not have_gm and not borked:
        dm_tm = await TidyMessage.build(ctx, get_escape(ctx), content=st.ASK_IF_GM, dest=return_member(gm).dm_channel,
                                        checks=[check_alias_f(alias.CONFIRM_ALIASES),
                                                check_args_f("==", 1)])
        result = dm_tm.message.content
        if result.content.lower() in alias.AFFIRM:
            await dm_tm.rebuild(st.YOUR_FUNERAL)
            have_gm = True
        elif result.content.lower() in alias.DENY:
            await dm_tm.rebuild(st.INF_NOT_GM)
            borked = True

    # If GM denied the lofty position, let the caller know.
    if borked:
        return tm.rebuild(st.INF_DENIED_GM)

    # Make category for the canon to reside in.
    category = await ctx.guild.create_category(canon)

    # Make folder, initial docs and roles.
    canons_dir = "model\\" + str(ctx.guild.id) + "\\" + st.CANONS_FN
    arch_dir = canons_dir + "\\" + st.ARCHIVES_FN
    canon_dir = canons_dir + "\\" + str(category.id)
    if not os.path.exists(canon_dir):
        # Prepare all directories.
        if not os.path.exists(arch_dir):
            os.makedirs(arch_dir)
        os.makedirs(canon_dir + "\\" + st.CHARACTERS_FN)
        os.makedirs(canon_dir + "\\" + st.LOGS_FN)
        os.makedirs(canon_dir + "\\" + st.META_FN)
        pref_dir = canon_dir + "\\" + st.PLAYER_PREFS_FN
        os.makedirs(pref_dir)

        # Make a file to handle the command exceptions
        except_dir = canon_dir + "\\" + st.META_FN + "\\" + st.EXCEPTIONS_FN
        open(except_dir, "a").close()
        with open(except_dir, "w") as fout:
            json.dump({}, fout, indent=1)

        # Make roles to discern who can do what.
        role, r_dat = list(), dict()
        for n in UserType:
            r = await ctx.guild.create_role(name=canon.upper() + " " + str(n).upper())
            role.append(r)
            r_dat[r.name] = r.id

        # Record the role ids for later access.
        role_dir, role_ids = canon_dir + "\\" + st.META_FN + "\\" + st.ROLES_FN, {}
        open(role_dir, "a").close()
        with open(role_dir, "w") as fout:
            for r in role:
                role_type = r.name.split()[1]
                role_ids[role_type] = r.id
            json.dump(role_ids, fout, indent=1)

        # For each member in the channel, make a file and add them to the proper role.
        for mem in ctx.guild.members:
            player_pref = pref_dir + "\\" + str(mem.id) + ".json"
            with open(player_pref, "a") as fout:
                if gm[0] == mem.mention:
                    pref = {"user_type": UserType.GM.value, "relevant_character": None}
                    await mem.add_roles(role[2])
                else:
                    pref = {"user_type": UserType.OBSERVER.value, "relevant_character": None}
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
        c = ["_IC", "_OOC", "_command_room", "_rules", "_meta", "_gm_notes"]
        c_dat = dict()

        # IC Channel is locked on creation.
        channel = await ctx.guild.create_text_channel(canon + c[0], category=category,
                                                      overwrites={role[0]: r, role[1]: r, role[2]: r})
        c_dat[channel.name] = channel.id

        # OOC Channel is open to all on creation.
        channel = await ctx.guild.create_text_channel(canon + c[1], category=category,
                                                      overwrites={role[0]: rw, role[1]: rw, role[2]: rw})
        c_dat[channel.name] = channel.id

        # Command Room is open only to players and the gm.
        channel = await ctx.guild.create_text_channel(canon + c[2], category=category,
                                                      overwrites={role[0]: n, role[1]: rw, role[2]: rw})
        c_dat[channel.name] = channel.id

        # Rules is for posting that which people should follow that the bot doesn't enforce.
        channel = await ctx.guild.create_text_channel(canon + c[3], category=category,
                                                      overwrites={role[0]: r, role[1]: r, role[2]: rw})
        c_dat[channel.name] = channel.id

        # Meta is for viewing the meta-rules of the canon only. The GM only affects these indirectly.
        channel = await ctx.guild.create_text_channel(canon + c[4], category=category,
                                                      overwrites={role[0]: r, role[1]: r, role[2]: r})
        c_dat[channel.name] = channel.id

        # GM Notes is for the gm's eyes only.
        channel = await ctx.guild.create_text_channel(canon + c[5], category=category,
                                                      overwrites={role[0]: n, role[1]: n, role[2]: rw})
        c_dat[channel.name] = channel.id

        # Record untouchable instance of data.
        meta_dir = canon_dir + "\\" + st.META_FN + "\\" + str(st.IDS_FN)
        with open(meta_dir, "a") as fout:
            json.dump({"channels": c_dat, "roles": r_dat}, fout, indent=1)

    tm.rebuild(status)


# TODO: Test
async def delete_canon(ctx):
    """Deletes a canon and archives its data in case its remade."""
    # Initialize a tm.
    tm = await TidyMessage.build(ctx, get_escape(ctx), req=False, content=st.INF_MESSAGING_D)

    # Collect all players in canon.
    players = list()

    if not get_canon(ctx):
        return TidyMessage.build(ctx, get_escape(ctx), req=False, content=st.ERR_CANON_NONEXIST,
                                 mode=TidyMode.WARNING)

    # Prepare categories.
    yes, no = 1, 0  # Yes starts at one because the caller of the function is presumed to support deletion.

    # Tally up all participants in this canon.
    for mem in ctx.guild.members:
        user = get_user_type(mem, ctx.channel)
        if user == UserType.PLAYER.value or user == UserType.GM.value and mem != ctx.author:
            players.append(mem)

    # Notify users.
    affirmations, pool = list(), ThreadPool()
    for mem in players:
        if not mem.dm_channel:
            await mem.create_dm()
        affirmations.append(asyncio.ensure_future(wait_for_affirmation(ctx, mem.dm_channel, st.ASK_IF_DELETE)))

    # Await results...
    majority = math.ceil((len(players) + yes) / 2)
    while yes < majority and no < majority:
        done, affirmations = await tasks.wait(affirmations, return_when=asyncio.FIRST_COMPLETED)
        for d in done:
            if d.result().message.content.lower() in alias.AFFIRM:
                yes += 1
            elif d.result().message.content.lower() in alias.DENY:
                no += 1

    # Process results.
    if majority <= yes:
        # Prepare the directory we're going to move.
        canon_dir = "model\\" \
                    + str(ctx.guild.id) + "\\" \
                    + st.CANONS_FN + "\\" \
                    + str(ctx.channel.category_id)

        # Delete categories and roles in list.
        meta_dir = canon_dir + "\\" \
                   + st.META_FN + "\\" \
                   + st.IDS_FN

        guild_name = ctx.guild.get_channel(ctx.channel.category_id).name

        with open(meta_dir, "r") as fout:
            ids_json = json.load(fout)
            for c in ctx.guild.channels:
                if c.category_id == ctx.channel.category_id and ids_json["channels"].get(c.name):
                    await c.delete(reason=st.INF_DELETE_CHANNEL)

            for r in ctx.guild.roles:
                if ids_json["roles"].get(r.name):
                    await r.delete(reason=st.INF_DELETE_ROLE)

            for c in ctx.guild.channels:
                if c.id == ctx.channel.category_id:
                    await c.delete()
                    break

        # Move canon data to _archive
        arch_dir = "model\\" \
                   + str(ctx.guild.id) + "\\" \
                   + st.CANONS_FN + "\\" \
                   + st.ARCHIVES_FN + "\\" \
                   + guild_name
        os.rename(canon_dir, arch_dir)

    elif no >= majority and yes >= majority or yes < majority and no < majority:
        tm.rebuild(st.ERR_VOTE_FAILED, mode=TidyMode.WARNING)
    else:
        tm.rebuild(st.INF_DENIED_DELETE)


# TODO: Test
async def add_character(ctx):
    """A function to store a JSON entry of a character"""
    # Initialize a tm.
    tm = await TidyMessage.build(ctx, get_escape(ctx))

    # By default, the author of the character is the caller.
    author = tm.message.author

    # GMs can assign users characters.
    caller_is_gm = get_user_type(ctx.message.author, ctx.channel) == UserType.GM

    if caller_is_gm:
        # Ask which player this is for.
        player_undecided = True

        while player_undecided:
            tm = await tm.rebuild(st.REQ_PLAYER,
                                  checks=[check_invalid_f(val.WHITESPACE)])
            if tm == get_escape(ctx):
                return get_escape(ctx)

            # Convert mention to member instance.
            player = return_member(ctx, tm.message.content)

            # Check if player exists/isn't an observer
            if player is None:
                await s(ctx, st.ERR_NOT_IN_GUILD + " " + st.ERR_REPEAT_1)
            if get_user_type(ctx, player, ctx.channel) == UserType.OBSERVER.value:
                await s(ctx, st.ERR_NOT_IN_RP + " " + st.ERR_REPEAT_2)
            else:
                # Now we know to associate the character with this player.
                author = player
                player_undecided = False

    character_stats = ["NAME", "ATHLETICS", "CHARISMA", "DEXTERITY", "ACADEMICS", "SAVVY"]

    # Ask for stat values.
    for field in character_stats:
        # Prime the pump.
        input_not_recorded, repeat = True, ""
        while input_not_recorded:
            # Ask user for a field.
            tm = await tm.rebuild(repeat + st.REQ_CHARACTER.format(field),
                                  checks=[check_args_f("==", 1)])
            if tm == get_escape(ctx):
                return get_escape(ctx)
            # List of checks to make sure their input makes sense.
            if field == "NAME":
                # Store the name of the character.
                character = get_character_json(tm.message.content, ctx.channel)
                if character != {}:
                    repeat = st.ERR_PLAYER_EXIST
                else:
                    # Set initial fields.
                    character["PLAYER"] = author.id
                    character[field] = tm.message.content
                    input_not_recorded = False
            elif calc.is_int(tm.message.content):
                stat_val = int(tm.message.content)
                if not stat_val > -1:  # Inform the user that -1 or less might be a bit low.
                    repeat = st.ERR_STAT_LT_ZERO + " "
                elif not stat_val < 15:  # Inform the user that 16 or more is too high.
                    repeat = st.ERR_STAT_GT_FIFT + " "
                else:  # User got it right, make sure to break this loop.
                    character[field] = tm.message.content
                    input_not_recorded = False
            else:
                repeat = st.ERR_INV_FORM + " "

    # Confirm that the data is saved.
    tm.rebuild(st.SAVED + " " + st.rand_slack())

    # Update character file.
    character_file = "model\\" \
                     + str(ctx.guild.id) + "\\" \
                     + st.CANONS_FN + "\\" \
                     + str(ctx.channel.category_id) + "\\" \
                     + st.CHARACTERS_FN + "\\" \
                     + character["NAME"] + ".json"
    with open(character_file, "w") as fout:
        json.dump(character, fout, indent=1)

    # Update player prefs.
    prefs = get_prefs(author, ctx.channel)
    prefs["relevant_character"] = character["NAME"]
    prefs_file = "model\\" \
                 + str(ctx.guild.id) + "\\" \
                 + st.CANONS_FN + "\\" \
                 + str(ctx.channel.category_id) + "\\" \
                 + st.PLAYER_PREFS_FN + "\\" \
                 + str(author.id) + ".json"
    with open(prefs_file, "w") as fout:
        json.dump(prefs, fout, indent=1)


# TODO: Test
async def get_characters(ctx):

    canon_path = get_canon(ctx)

    if not canon_path:
        return TidyMessage.build(ctx, get_escape(ctx), req=False, content=st.ERR_NOT_IN_CANON, mode=TidyMode.WARNING)

    # Load in file.
    c_names, c_json = os.listdir(canon_path + "\\" + st.CHARACTERS_FN), {}
    for c in c_names:
        with open(canon_path + "\\" + st.CHARACTERS_FN + "\\" + c, "r") as fout:
            c_json[c] = json.load(fout)

    # Concatenate all names.
    all_names = "Character Names: \n"

    for key in c_names:
        all_names += '~ ' + c_json[key]["NAME"] + '\n'

    return await TidyMessage.build(ctx, get_escape(ctx), req=False, content=all_names, mode=TidyMode.WARNING)


# TODO: Test
async def perform_skill_roll(ctx):
    """Performs a basic skill roll."""
    #  ASK FOR BASIC INFO  #
    # Request roll purpose.
    tm = await TidyMessage.build(ctx, get_escape(ctx), content=st.REQ_ROLL_PURPOSE)
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)
    purpose = tm.message.content

    # Find the related character.
    tm = await tm.rebuild(st.REQ_ACTIVE_CHARACTER,
                          checks=[check_args_f("==", 1)])
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)
    character = get_character_json(tm.message.content, ctx.channel)

    # Request stats for roll.
    tm = await tm.rebuild(st.REQ_STATS,
                          checks=[check_alias_f(alias.STATS_ALIASES, no_dups=True),
                                  check_args_f("<=", 2)])
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)
    stats = shlex.split(tm.message.content)

    #  ASK FOR MODS  #
    # Define Lists
    mod_r, mod_v = [], []  # Reasons, Values

    # Ask for confirmation on modifiers.
    tm = tm.rebuild(st.ASK_IF_MODS,
                    checks=[check_alias_f(alias.CONFIRM_ALIASES),
                            check_args_f("==", 1)])
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)
    confirm = tm.message.content

    # Check confirm status.
    while confirm.lower() in alias.AFFIRM:
        # Request mod reason.
        tm = tm.rebuild(st.ASK_IF_MODS,
                        checks=[check_alias_f(alias.STATS_ALIASES),
                                check_args_f("==", 1)])
        if tm.message.content == get_escape(ctx):
            return get_escape(ctx)
        mod_r.append(tm.message.content)

        # Request mod amount.
        tm = tm.rebuild(st.ASK_IF_MODS,
                        checks=[check_alias_f(alias.STATS_ALIASES),
                                check_args_f("==", 1),
                                check_int])
        if tm.message.content == get_escape(ctx):
            return get_escape(ctx)

        mod_v.append(tm.message.content)

        # Ask if more mods.
        tm = tm.rebuild(st.ASK_IF_MODS,
                        checks=[check_alias_f(alias.CONFIRM_ALIASES),
                                check_args_f("==", 1)])
        if tm == get_escape(ctx):
            return get_escape(ctx)
        confirm = tm.message.content

    #  COMPLETE THE ROLL  #
    norm_stat_types, dice_pool = [], 0

    # Collect roll information.
    for stat in stats:
        norm_stat_types.append(redeem_alias(stat, alias.STATS_ALIASES))
    for stat in norm_stat_types:
        dice_pool += int(character[stat])
    base_pool = dice_pool
    for mod in mod_v:
        dice_pool += int(mod)

    # Roll the die and make the string.
    successes = calc.skill_roll(dice_pool)
    final_string = st.skill_roll_string(mod_r, mod_v, dice_pool, base_pool, purpose,
                                        norm_stat_types, stats, successes)

    # Print the final string.
    tm.rebuild("Here it is. Go wild. \n\n" + final_string)


async def new_combat(ctx):
    """Begins a combat by opening the relevant channels"""
    # Prepare canon file path.
    canon = "model\\" \
            + str(ctx.guild.id) + "\\" \
            + st.CANONS_FN + "\\" \
            + str(ctx.channel.category_id)

    # Ask for players.
    tm = TidyMessage.build(ctx, get_escape(ctx), content=st.REQ_USER_COMBAT,
                           checks=[check_member_f(ctx),
                                   check_args_f(">=", 2)])
    if tm.message.content == get_escape(ctx):
        return get_escape(ctx)
    players = shlex.split(tm.message.content)

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
            if not return_member(ctx, mem):
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
    if op == ">":
        def check(*args):
            return True if len(args) > num else st.ERR_TOO_FEW_ARGS.format("more than", str(num))
    elif op == ">=":
        def check(*args):
            return True if len(args) >= num else st.ERR_TOO_FEW_ARGS.format(str(num), "or more")
    elif op == "<":
        def check(*args):
            return True if len(args) < num else st.ERR_TOO_MANY_ARGS.format("less than", str(num))
    elif op == "<=":
        def check(*args):
            return True if len(args) <= num else st.ERR_TOO_MANY_ARGS.format(str(num), "or less")
    elif op == "==":
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
                    print(al.lower() == a.lower())
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


async def wait_for_affirmation(ctx, channel, content):
    """Method to encapsulate all parts of asking if someone is joining in a combat."""
    return TidyMessage.build(ctx, get_escape(ctx), dest=channel, content=content,
                             checks=[check_alias_f(alias.CONFIRM_ALIASES),
                                     check_args_f("==", 1)])


# Utility #


def check_perms(ctx, command=""):
    """Provides information about command relative to the member calling the command."""
    # Collect the command name.
    command = command if command else ctx.command.name

    if get_canon(ctx) and val.perms[command]:
        # Check role of player against those allowed to call command.
        can_call = get_user_type(ctx.message.author, ctx.channel) in val.perms[command]

        # Check if on exception list.
        meta_dir = "model\\" \
                   + str(ctx.guild.id) + "\\" \
                   + st.CANONS_FN + "\\" \
                   + str(ctx.channel.category_id) + "\\" \
                   + st.META_FN + "\\" \
                   + st.EXCEPTIONS_FN
        with open(meta_dir, "r") as fout:
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


def make_general_player_prefs(guild):
    """Initializes the player prefs if they don't exist."""
    # Make folder and initial docs if they don't exist.
    pref_dir = "model\\" \
               + str(guild.id) + "\\" \
               + st.GENERAL_FN + "\\" \
               + st.PLAYER_PREFS_FN
    if not os.path.exists(pref_dir):
        os.makedirs(pref_dir)

    # For each member in the channel, make a file.
    for mem in guild.members:
        player_pref = pref_dir + "\\" + str(mem.id) + ".json"
        if not os.path.exists(player_pref):
            with open(player_pref, "a") as fout:
                pref = {"escape": '~'}
                json.dump(pref, fout, indent=1)


def get_prefs(member, channel):
    """Returns the prefs of the user as a JSON."""
    pref_path = "model\\" \
                + str(channel.guild.id) + "\\" \
                + st.CANONS_FN + "\\" \
                + str(channel.category_id) + "\\" \
                + st.PLAYER_PREFS_FN + "\\" \
                + str(member.id) + ".json"
    if os.path.exists(pref_path):
        with open(pref_path, "r") as fin:
            prefs = json.load(fin)
        return prefs
    return None


def get_canon(ctx):
    """Returns the category file path or None of doesn't exist."""
    if ctx.channel.category_id:
        canon = "model\\" + str(ctx.guild.id) + "\\" + st.CANONS_FN + "\\" + str(ctx.channel.category_id)
        return canon if os.path.exists(canon) else None


def get_user_type(member, channel):
    """Returns the usertype of a member relative to the channel being called from."""
    return get_prefs(member, channel).get("user_type")


def get_character_json(character, channel):
    """Returns an object with all character values in it."""
    # Pull JSON file for reading.
    character_file = "model\\" \
                     + st.CANONS_FN + "\\" \
                     + str(channel.category_id) + "\\" \
                     + st.CHARACTERS_FN + "\\" \
                     + character
    open(character_file, "a").close()
    with open(character_file, "r") as fin:
        if os.stat(character_file).st_size > 0:
            a = json.load(fin)
        else:
            a = {}
    return a


def redeem_alias(alias_i, aliases):
    """Returns the normalized form (first element in the list) of an alias value"""
    # Compare alias to other aliases
    for a in aliases:
        for value in aliases[a]:
            if value.lower() == alias_i.lower():
                return aliases[a][0]
    return None


def return_member(ctx, mention, user_id=""):
    """Returns the user by mention or None, if none found. If an ID is provided, returns based off of that instead."""

    # # If ID provided, return what the bot would return. # #

    if user_id:
        return val.bot.get_user(user_id)

    # # If no ID provided, return based on mention. # #

    # Link members to their mentions.
    members = {}
    for mem in ctx.guild.members:
        members[mem.mention] = mem

    return members.get(mention)


def get_escape(ctx):
    """Get the escape value of a member."""
    pref_dir = "model\\" \
               + str(ctx.guild.id) + "\\" \
               + st.GENERAL_FN + "\\" \
               + st.PLAYER_PREFS_FN + "\\" \
               + str(ctx.author.id) + ".json"

    with open(pref_dir, "r") as fin:
        pref_json = json.load(fin)

    return pref_json["escape"]


def set_escape(ctx, escape):
    """Set the escape value of a member."""
    pref_dir = "model\\" \
               + str(ctx.guild.id) + "\\" \
               + st.GENERAL_FN + "\\" \
               + st.PLAYER_PREFS_FN + "\\" \
               + str(ctx.author.id) + ".json"

    escape_json = {"escape": escape}

    with open(pref_dir, "w") as fout:
        json.dump(escape_json, fout, indent=1)


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


def get_app_token():
    with open('token.txt', 'r') as token:
        token = token.read()
    return token

# Syntactical Candy #


def s(ctx, arg):
    """Syntactical candy:  sends a message."""
    return ctx.channel.send(content=arg)


def t(target, arg):
    """Syntactical candy:  sends a message to a location (typically a user)."""
    return target.send(content=arg)
