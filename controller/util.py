# ----------- Script by ReedRGale ----------- #
# Utility functions that lubricate the process of... a lot of things. #


# Import #

import json
import os
import re
import discord
import math
import asyncio

from asyncio import tasks, futures, coroutines
from multiprocessing.pool import ThreadPool
from model import st, alias, reg, val
from model.enums import UserType
from controller import calc


# Command Encapsulations #


async def add_character(ctx):
    """A function to store a JSON entry of a character"""
    # GMs can assign users characters.
    caller_is_gm = get_user_type(ctx.message.author, ctx.channel) == UserType.GM

    if caller_is_gm:
        # Ask which player this is for.
        player_undecided = True

        while player_undecided:
            rsp = await req(ctx, st.REQ_PLAYER, f_strip, expected_vars=1)
            if rsp == get_escape(ctx):
                return get_escape(ctx)

            # Convert player to member instance.
            player = return_member(rsp[0])

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

        input_not_recorded = True

        # Loop to not have to repeat the command over and over if an input is wrong.
        while input_not_recorded:
            # Ask user for each field.
            stat = await req(ctx, st.REQ_CHARACTER + field + " value:", f_none, expected_vars=1)
            if stat == get_escape(ctx):
                return get_escape(ctx)

            # List of checks to make sure their input makes sense.
            if field == "NAME":
                # Store the name of the character.
                character = get_character_json(stat[0], ctx.channel)
                if character != {}:
                    await s(ctx, st.ERR_PLAYER_EXIST + " " + st.rand_slack())
                    return get_escape(ctx)

                # Set initial fields.
                character["PLAYER"] = author.id
                character[field] = stat[0]

                input_not_recorded = False

            elif field != "NAME" and calc.is_int(stat[0]):
                stat_val = int(stat[0])
                non_neg = stat_val > -1
                lt_fift = stat_val < 15

                # Inform the user that -1 or less might be a bit low.
                if not non_neg:
                    await s(ctx, st.ERR_STAT_LT_ZERO)

                # Inform the user that 16 or more is too high.
                if not lt_fift:
                    await s(ctx, st.ERR_STAT_GT_FIFT)

                # User got it right, make sure to break this loop.
                if non_neg and lt_fift:
                    character[field] = stat[0]
                    input_not_recorded = False

            elif field != "NAME" and not calc.is_int(stat[0]):
                await s(ctx, st.ERR_INV_FORM)

    # Update character file.
    character_file = "model\\" \
                     + str(ctx.guild.id) + "\\" \
                     + st.CANONS_FN + "\\" \
                     + str(ctx.channel.category_id) + "\\" \
                     + st.CHARACTERS_FN + "\\" \
                     + character["NAME"]
    with open(character_file + ".json", "w") as fout:
        json.dump(character, fout, indent=1)

    # Update player prefs.
    prefs = get_prefs(ctx, author, ctx.channel)
    prefs["relevant_character"] = character["NAME"]
    canon = "model\\" \
            + str(ctx.guild.id) + "\\" \
            + st.CANONS_FN + "\\" \
            + str(ctx.channel.category_id) + "\\" \
            + st.PLAYER_PREFS_FN + "\\"
    with open(canon + "\\" + str(author.id) + ".json", "w") as fout:
        json.dump(prefs, fout, indent=1)


def get_characters(ctx):

    canon_path = get_canon(ctx)

    if not canon_path:
        return st.ERR_NOT_IN_CANON

    # Load in file.
    c_names, c_json = os.listdir(canon_path + "\\" + st.CHARACTERS_FN), {}
    for c in c_names:
        with open(canon_path + "\\" + st.CHARACTERS_FN + "\\" + c, "r") as fout:
            c_json[c] = json.load(fout)

    # Concatenate all names.
    all_names = "Character Names: \n"

    for key in c_names:
        all_names += '► ' + c_json[key]["NAME"] + '\n'

    return all_names


async def perform_skill_roll(ctx):
    """Performs a basic skill roll."""
    # Request roll purpose.
    purpose = await req(ctx, st.REQ_ROLL_PURPOSE, f_none, expected_vars=1)
    if purpose == get_escape(ctx):
        return get_escape(ctx)

    # Find the related character.
    character = await req(ctx, st.REQ_ACTIVE_CHARACTER, f_none, expected_vars=1)
    character = get_character_json(character[0], ctx.channel)

    # Request stats for roll.
    stats = await check_against_alias(ctx, st.REQ_STATS, alias.STATS_ALIASES, f_alpha, expected_vars=2)
    if stats == get_escape(ctx):
        return get_escape(ctx)

    # Retrieve mods.
    mod = await ask_for_mods(ctx)
    if mod == get_escape(ctx):
        return get_escape(ctx)

    # Allocate mod particulates to proper locations.
    mod_r, mod_v = mod[0], mod[1]  # Reasons, Values

    # Complete the roll.
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

    return final_string


async def new_combat(ctx):
    """Begins a combat by opening the relevant channels"""
    # Prepare canon file path.
    canon = "model\\" \
            + str(ctx.guild.id) + "\\" \
            + st.CANONS_FN + "\\" \
            + str(ctx.channel.category_id)

    # Ask for players.
    players = req_user(ctx, st.REQ_USER_COMBAT, 2, error=st.ERR_INV_FORM)
    if players == get_escape(ctx):
        return get_escape(ctx)

    # Notify users.
    async_results, pool = dict(), ThreadPool(processes=len(players))

    for mem in players:
        dm = return_member(mem).dm_channel
        await t(dm, st.ASK_IF_FIGHT)
        async_results[mem] = pool.apply_async(wait_for_affirmation, (ctx, return_member(mem), dm))

    # Process results...
    accounted_for = []
    queued = []
    borked = False

    while async_results and not borked:
        for mem in players:
            if async_results[mem].get() in alias.AFFIRM:
                queued.append(mem)
            elif async_results[mem].get() in alias.DENY:
                borked = True
        for v in queued:
            accounted_for.append(v)
            del players[v]

    for af in accounted_for:
        # Make private channels and assign roles to given players/GM.
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            players[af]: discord.PermissionOverwrite(read_messages=True)
        }
        await ctx.guild.create_text_channel("Test_Guild", overwrites=overwrites)
        await t(players[af].dm_channel, st.INF_CHANNELS_MADE)


async def make_canon(ctx):
    """Makes a canon folder and files."""
    # Ask for RP name
    canon = await req(ctx, st.REQ_NEW_CANON, f_none, expected_vars=1)
    if canon == get_escape(ctx):
        return get_escape(ctx)

    canon = canon[0].replace(" ", "_")

    # Ask for GM.
    gm = await req_user(ctx, st.REQ_USER_GM, 1, error=(st.ERR_ONLY_ONE_GM + ' ' + st.ERR_REPEAT_1), log_op="<=")
    if gm == get_escape(ctx):
        return get_escape(ctx)
    have_gm = gm[0] == ctx.author.mention
    borked = False

    # If the GM isn't the maker of the canon, ask them if they want to take on this hell.
    while not have_gm and not borked:
        priv = await t(return_member(gm[0]), st.ASK_IF_GM)
        result = await priv.channel.wait_for("message")
        if result.content.lower() in alias.AFFIRM:
            await t(return_member(gm[0]), st.YOUR_FUNERAL)
            have_gm = True
        elif result.content.lower() in alias.DENY:
            await t(return_member(gm[0]), st.INF_NOT_GM)
            borked = True
        else:
            await t(return_member(gm[0]), st.ERR_INV_FORM)

    # If GM denied the lofty position, let the caller know.
    if borked:
        return st.INF_DENIED_GM

    # Make roles to discern who can do what.
    role, r_dat = list(), dict()
    for n in UserType:
        r = await ctx.guild.create_role(name=canon.upper() + " " + str(n).upper())
        role.append(r)
        r_dat[r.name] = r.id

    # Make category for the canon to reside in.
    category = await ctx.guild.create_category(canon)

    # Make folder and initial docs
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

    return status


async def delete_canon(ctx):
    """Deletes a canon and archives its data in case its remade."""
    # Collect all players in canon.
    players = list()

    # Prepare categories.
    yes, no = 0, 0

    if not get_canon(ctx):
        return st.ERR_CANON_NONEXIST

    for mem in ctx.guild.members:
        user = get_user_type(mem, ctx.channel)
        if user == UserType.PLAYER.value:
            players.append(mem)
        if user == UserType.GM.value:
            yes += 1

    # Notify users.
    affirmations, pool = list(), ThreadPool()

    for mem in players:
        if not mem.dm_channel:
            await mem.create_dm()
        await t(mem.dm_channel, st.ASK_IF_DELETE)
        affirmations.append(asyncio.ensure_future(wait_for_affirmation(ctx, mem, mem.dm_channel)))

    # Process results...
    majority = math.ceil((len(players) + yes) / 2)

    while yes < majority and no < majority:
        done, affirmations = await tasks.wait(affirmations, return_when=asyncio.FIRST_COMPLETED)

        for d in done:
            if d.result().lower() in alias.AFFIRM:
                yes += 1
            elif d.result().lower() in alias.DENY:
                no += 1

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
        return st.ERR_VOTE_FAILED
    else:
        return st.INF_DENIED_DELETE

# Formatters #


async def f_alpha(ctx, command_info, array, expected_vars, log_op="<="):
    """A formatting helper method that makes sure that a string is only alphabetical.
    Read log_op as:  I expect the arguments to be <log_op> <expected_vars>."""
    improperly_formatted = True

    # Define proper check.
    a = ctx.author
    c = ctx.channel

    def check(resp): return resp.author == a and resp.channel == c

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == get_escape(ctx):
            await s(ctx, st.ESCAPE)
            return get_escape(ctx)

        # Check to make sure they didn't try to screw things up.
        if log_op == "<=" and len(array) > expected_vars:
            improperly_formatted = True
            await s(ctx, st.ERR_EXTRA_ARGS + str(expected_vars) + " or less. " + st.ERR_REPEAT_1)
            formatted_rsp = await val.bot.wait_for("message", check=check)
            array = formatted_rsp.content.split()
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(ctx, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT_1)
            formatted_rsp = await val.bot.wait_for("message", check=check)
            array = formatted_rsp.content.split()

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(reg.non_alphabetic, '', array[j])

    return array


async def f_numer(ctx, command_info, array, expected_vars, log_op='<='):
    """A formatting helper method that makes sure that a string is only numeric."""
    # Read log_op as:  I expect the arguments to be <log_op> <expected_vars>.
    improperly_formatted = True

    # Define proper check.
    a = ctx.author
    c = ctx.channel

    def check(resp): return resp.author == a and resp.channel == c

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == get_escape(ctx):
            await s(ctx, st.ESCAPE)
            return get_escape(ctx)

        # Check to make sure they didn't try to screw things up.
        if log_op == "<=" and len(array) > expected_vars:
            improperly_formatted = True
            await s(ctx, st.ERR_EXTRA_ARGS + str(expected_vars) + " or less. " + st.ERR_REPEAT_1)
            formatted_rsp = await val.bot.wait_for("message", check=check)
            array = formatted_rsp.content.split()
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(ctx, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT_1)
            formatted_rsp = await val.bot.wait_for("message", check=check)
            array = formatted_rsp.content.split()

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(reg.non_numeric, '', array[j])

    return array


async def f_none(ctx, command_info, array, expected_vars=1, log_op="<="):
    """A formatting helper method that makes sure that a set of values is only so many arguments."""
    # Read log_op as:  I expect the arguments to be <log_op> <expected_vars>.
    improperly_formatted = True

    # Define proper check.
    a = ctx.author
    c = ctx.channel

    def check(resp): return resp.author == a and resp.channel == c

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == get_escape(ctx):
            await s(ctx, st.ESCAPE)
            return get_escape(ctx)

        single_statement = [""]

        # Concatenate if they had a comma. Basically, glue it back together. Elegiggle.
        if log_op == "<=" and len(array) > expected_vars:
            for bucket in len(array):
                single_statement[0] += bucket if bucket != len(array) - 1 else bucket + ','
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(ctx, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT_1)
            formatted_rsp = await val.bot.wait_for("message", check=check)
            array = formatted_rsp.content.split()
        else:
            single_statement = array

    return single_statement


async def f_strip(ctx, command_info, array, expected_vars, log_op='<='):
    """A formatting helper method that makes sure that a string is only numeric."""
    # Read log_op as:  I expect the arguments to be <log_op> <expected_vars>.
    improperly_formatted = True

    # Define proper check.
    a = ctx.author
    c = ctx.channel

    def check(resp): return resp.author == a and resp.channel == c

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == get_escape(ctx):
            await s(ctx, st.ESCAPE)
            return get_escape(ctx)

        # Check to make sure they didn't try to screw things up.
        if log_op == "<=" and len(array) > expected_vars:
            improperly_formatted = True
            await s(ctx, st.ERR_EXTRA_ARGS + str(expected_vars) + " or less. " + st.ERR_REPEAT_1)
            formatted_rsp = await val.bot.wait_for("message", check=check)
            array = formatted_rsp.content.split()
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(ctx, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT_1)
            formatted_rsp = await val.bot.wait_for("message", check=check)
            array = formatted_rsp.content.split()

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = array[j].strip()

    return array


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


def get_canon(ctx):
    """Returns the category file path or None of doesn't exist."""
    if ctx.channel.category_id:
        canon = "model\\" + str(ctx.guild.id) + "\\" + st.CANONS_FN + "\\" + str(ctx.channel.category_id)
        return canon if os.path.exists(canon) else None


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


async def ask_for_mods(ctx):
    """Asks the user if they would like to add modifications to a roll."""
    # Define Lists
    mod_r, mod_v = [], []  # Reasons, Values

    # Ask for confirmation on modifiers.
    confirm = await check_against_alias(ctx, st.ASK_IF_MODS, alias.CONFIRM_ALIASES, f_alpha, expected_vars=1)
    if confirm == get_escape(ctx):
        return get_escape(ctx)

    # Check confirm status.
    while confirm[0].lower() in alias.AFFIRM:
        # Request mod reason.
        reason = await req(ctx, st.REQ_MOD_REASON, f_none, expected_vars=1)
        if reason == get_escape(ctx):
            return get_escape(ctx)
        mod_r.append(reason[0])

        no_int = True  # No proper input yet given.

        while no_int:
            # Request mod amount.
            amount = await req(ctx, st.REQ_MOD_AMOUNT, f_numer, expected_vars=1)
            if amount == get_escape(ctx):
                return get_escape(ctx)
            no_int = not calc.is_int(amount[0])
            if no_int:
                await s(ctx, st.ERR_INV_FORM)

        mod_v.append(amount[0])

        # Ask if more mods.
        confirm = await check_against_alias(ctx, st.ASK_IF_MORE_MODS, alias.CONFIRM_ALIASES,
                                            f_alpha, expected_vars=1)
        if confirm == get_escape(ctx):
            return get_escape(ctx)

    return [mod_r, mod_v]


async def check_against_alias(ctx, request_str, aliases, formatter, expected_vars):
    """Compares a set of aliases [a dictionary of lists] to a list of values"""
    # Prime the pump.
    i, used = 0, []
    values = await req(ctx, request_str, formatter, expected_vars)
    if values == get_escape(ctx):
        return get_escape(ctx)

    # For each possible alias, check that the names the user input are valid.
    while i < len(values):
        invalid = True
        for name in aliases:
            for a in aliases[name]:
                if a.lower() == values[i].lower() and name not in used:  # Alias found & not used prev.
                    invalid = False
                    used.append(name)
                elif a.lower() == values[i].lower() and name in used:  # Alias found & used prev.
                    # Inform the user that they've repeated an argument.
                    await s(ctx, st.ERR_REPEAT_ARG + values[i] + "!")
                    invalid = False
                    # Reprime the pump.
                    i, used = 0, []
                    values = await req(ctx, st.ERR_REPEAT_1, formatter, expected_vars)
                    if values == get_escape(ctx):
                        return get_escape(ctx)
                    break
            if not invalid:
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(ctx, st.ERR_INV_ARG + values[i] + "!")
            # Reprime the pump.
            i, used = 0, []
            values = await req(ctx, st.ERR_REPEAT_1, formatter, expected_vars)
            if values == get_escape(ctx):
                return get_escape(ctx)

        else:  # Otherwise, alias found; continue.
            i += 1

    return values


async def check_against_list(ctx, request_str, comparators, formatter, expected_vars):
    """Compares a set of comparators to a list of values"""

    # Prime the pump.
    i, used = 0, []
    values = await req(ctx, request_str, formatter, expected_vars)
    if values == get_escape(ctx):
        return get_escape(ctx)

    # For each possible value, check that the names the user input are valid.
    while i < len(values):
        invalid = True
        for c in comparators:
            if c.lower() == values[i].lower() and c not in used:  # Value found & not used prev.
                invalid = False
                used.append(c)
                i += 1
                break
            elif c.lower() == values[i].lower() and c in used:  # Value found & used prev.
                # Inform the user that they've repeated an argument.
                await s(ctx, st.ERR_REPEAT_ARG + values[i] + "! " + st.ERR_REPEAT_1)
                invalid = False
                # Reprime the pump.
                i, used = 0, []
                values = await req(ctx, request_str, formatter, expected_vars)
                if values == get_escape(ctx):
                    return get_escape(ctx)
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(ctx, st.ERR_INV_ARG + values[i] + "! " + st.ERR_REPEAT_1)
            # Reprime the pump.
            i, used = 0, []
            values = await req(ctx, request_str, formatter, expected_vars)
            if values == get_escape(ctx):
                return get_escape(ctx)

    return values


async def wait_for_affirmation(ctx, author, channel):
    """Method to encapsulate all parts of asking if someone is joining in a combat."""
    affirmed = None

    # Go until confirmation acquired.
    while not affirmed:

        # Define check
        a = author
        c = channel

        def check(resp): return resp.author == a and resp.channel == c

        affirmed = await val.bot.wait_for("message", check=check)
        affirmed = affirmed.content
        if affirmed.lower() not in alias.AFFIRM and affirmed.lower() not in alias.DENY:
            affirmed = None
            await s(ctx, st.ERR_NOT_YES_OR_NO)

    return affirmed


async def req(ctx, req_str, formatter, expected_vars, log_op="<="):
    """Ask a request for the user and return that request as a list of inputs or return an escape character."""
    # Ask the request.
    await s(ctx, req_str)

    # Define check
    a = ctx.author
    c = ctx.channel

    def check(resp): return resp.author == a and resp.channel == c

    # Wait for response.
    rsp = await val.bot.wait_for("message", check=check)
    values = rsp.content.split()
    values = await formatter(ctx, rsp.content, values, expected_vars, log_op)
    if values == get_escape(ctx):
        return get_escape(ctx)
    return values


async def req_user(ctx, request_str, expected_vars, log_op=">=", error=st.ERR_INV_FORM):
    """Speeds up asking for a player."""
    mems = [""]  # Dummy data to prime the pump.
    while not members_exist(ctx, mems):
        mems = await req(ctx, request_str, f_none, expected_vars=expected_vars, log_op=log_op)
        if mems == get_escape(ctx):
            return get_escape(ctx)
        elif not members_exist(ctx, mems):
            await s(ctx, error)
    return mems


def members_exist(ctx, m_list):
    """Helper method to check to see if a set of members exist."""
    all_exist = True
    for mem in m_list:
        if not return_member(ctx, mem):
            all_exist = False
            break
    return all_exist


def get_escape(ctx):
    """Get the escape value of a member."""
    pref_dir = "model\\" \
               + str(ctx.guild.id) + "\\" \
               + st.GENERAL_FN + "\\" \
               + st.PLAYER_PREFS_FN + "\\" \
               + str(ctx.author.id) + ".json"

    with open(pref_dir, "r") as fout:
        pref_json = json.load(fout)

    return pref_json["escape"]


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
