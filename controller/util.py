# ----------- Script by ReedRGale ----------- #
# Utility functions that lubricate the process of... a lot of things. #
# TODO: Separate this out further if you get the chance. Might be hell though.


# Import #

import json
import os
import re
import discord

from multiprocessing.pool import ThreadPool
from model import st, alias, reg, val
from model.enums import UserType
from controller import calc


# Command Encapsulations #


async def add_character(m):
    """A function to store a JSON entry of a character"""
    # TODO: Change to ask for player if GM
    # TODO: Change to add player as character's maker if not GM
    # TODO: Set limit on characters a player can make

    # Ask for stat values.
    for field in val.focused_character:

        input_not_recorded = True

        # Loop to not have to repeat the command over and over if an input is wrong.
        while input_not_recorded:

            # Ask user for each field.
            await s(m, st.REQ_CHARACTER + field + " value:")
            stat_rsp = await val.client.wait_for_message(author=m.author)
            if stat_rsp.content == val.escape_value:
                return val.escape_value

            # List of checks to make sure their input makes sense.
            elif field != "NAME" and calc.is_int(stat_rsp.content):
                stat_val = int(stat_rsp.content)
                non_neg = stat_val > -1
                lt_fift = stat_val < 15

                # Inform the user that -1 or less might be a bit low.
                if not non_neg:
                    await s(m, st.ERR_STAT_LT_ZERO)

                # Inform the user that 16 or more is too high.
                if not lt_fift:
                    await s(m, st.ERR_STAT_GT_FIFT)

                # User got it right, make sure to break this loop.
                if non_neg and lt_fift:
                    val.focused_character[field] = stat_rsp.content
                    input_not_recorded = False

            elif field == "NAME":
                # Store the name of the character.
                val.focused_character[field] = stat_rsp.content
                input_not_recorded = False

            elif field != "NAME" and not calc.is_int(stat_rsp.content):
                await s(m, st.ERR_INV_FORM)

    # Make file if it doesn't exist.
    characters = get_characters()

    # Append character to file.
    characters[val.focused_character["NAME"]] = val.focused_character

    # Update character file.
    with open(val.rel_canon + "\\" + st.CHARACTERS_FILENAME, "w") as fout:
        json.dump(characters, fout, indent=1)


async def perform_skill_roll(m):
    """Performs a basic skill roll."""
    # Request roll purpose.
    purpose = await request_of_user(m, st.REQ_ROLL_PURPOSE,
                                    format_none, expected_vars=1)
    if purpose[0] == val.escape_value:
        return val.escape_value

    # Find the related character.
    # TODO: Skip this if relevant character is set for player.
    characters_json = get_characters()
    all_names = []
    for name in characters_json:
        all_names.append(name)
    characters = await user_input_against_list(m, st.REQ_ACTIVE_CHARACTER, all_names,
                                           format_alpha, expected_vars=1)
    if characters[0] == val.escape_value:
        return val.escape_value

    # Request stats for roll.
    stats = await user_input_against_aliases(m, st.REQ_STATS, alias.STATS_ALIASES,
                                             format_alpha, expected_vars=2)
    if stats[0] == val.escape_value:
        return val.escape_value

    # Ensure we have the correct json object.
    characters_json = characters_json[characters[0].title()]

    # Retrieve mods.
    mod = await ask_for_mods(m)
    if characters[0] == val.escape_value:
        return val.escape_value

    # Allocate mod particulates to proper locations.
    mod_r = mod[0]  # Reasons
    mod_v = mod[1]  # Values

    # Complete the roll.
    norm_stat_types = []
    dice_pool = 0

    # Collect roll information.
    for stat in stats:
        norm_stat_types.append(redeem_alias(stat, alias.STATS_ALIASES))

    for stat in norm_stat_types:
        dice_pool += int(characters_json[stat])

    base_pool = dice_pool

    for mod in mod_v:
        dice_pool += int(mod)

    # Roll the die and make the string.
    successes = calc.skill_roll(dice_pool)
    final_string = skill_roll_string(mod_r, mod_v, dice_pool, base_pool, purpose,
                                     norm_stat_types, stats, successes)

    return final_string


async def reg_combat(m):
    """Begins a combat by opening the relevant channels"""  # TODO: Test this.
    canon = '\n'
    users = []

    # Check canon exists.
    while not canon_exists(canon):
        canon = await request_of_user(m, st.REQ_CANON, format_none, expected_vars=1)
        if canon[0] == val.escape_value:
            return val.escape_value
        elif not canon_exists(canon):
            await s(m, st.ERR_INV_FORM)

    # TODO: Make this check by character, not player.
    # TODO: Add the GM if not already in the list.
    # Check player exists.
    users = ask_for_user(m, st.REQ_USER_COMBAT, 2, error=st.ERR_INV_FORM)
    if users[0] == val.escape_value:
        return val.escape_value

    # Collect all users.
    members = get_member_dict()

    # Notify users.
    async_results = {}

    for u in users:
        priv = await t(members[u], st.ASK_IF_FIGHT)
        pool = ThreadPool()
        async_results[u] = pool.apply_async(wait_for_combat_affirmation, (members[u], priv.channel))

    # Process results...
    accounted_for = []  # TODO: Add the player who called the command.
    queued = []
    borked = False

    while async_results and not borked:
        for i in range(len(users)):
            if async_results[users[i]].get() in alias.AFFIRM:
                queued.append(i)
            elif async_results[users[i]].get() in alias.DENY:
                borked = True
            # TODO: If in neither, send user an error message.
        for v in queued:
            accounted_for.append(users[v])
            del users[v]

    for af in accounted_for:
        # Make private channels and assign roles to given players/GM.
        everyone = discord.PermissionOverwrite(read_messages=False)
        theirs = discord.PermissionOverwrite(read_messages=True)
        await val.client.create_channel(m.server, "Test_Server",
                                        (m.server.default_role, everyone), (members[af], theirs))
        await val.client.send_message(members[af], st.INF_CHANNELS_MADE)

    # TODO: Begin combat interface in each channel.

async def make_canon(m, user):
    """Makes a canon folder and files."""
    # Ask for RP name
    canon = await request_of_user(m, st.REQ_NEW_CANON, format_none, expected_vars=1)
    if canon[0] == val.escape_value:
        return val.escape_value

    # Ask for GM.
    gm = await ask_for_user(m, st.REQ_USER_GM, 1, error=(st.ERR_ONLY_ONE_GM + ' ' + st.ERR_REPEAT), log_op="<=")
    if gm[0] == val.escape_value:
        return val.escape_value
    have_gm = gm[0] == user.mention
    borked = False

    # If the GM isn't the maker of the canon, ask them if they want to take on this hell.
    while not have_gm and not borked:
        members = get_member_dict()
        priv = await t(members[gm[0]], st.ASK_IF_GM)
        result = await val.client.wait_for_message(channel=priv.channel)
        if result.content in alias.AFFIRM:
            await t(members[gm[0]], st.YOUR_FUNERAL)
            have_gm = True
        elif result.content in alias.DENY:
            await t(members[gm[0]], st.INF_NOT_GM)
            borked = True
        else:
            await t(members[gm[0]], st.ERR_INV_FORM)

    # If GM denied the lofty position, let the caller know.
    if borked:
        return st.INF_DENIED_GM

    # Make roles to discern who can do what.
    roles = []
    for n in UserType:
        roles.append(await val.client.create_role(m.server, name=canon[0].title() + " " + str(n).upper()))

    # Make folder and initial docs
    canon_dir = "model\\canons\\" + canon[0]
    if not os.path.exists(canon_dir):
        os.makedirs(canon_dir)
        open(canon_dir + '\\' + st.CHARACTERS_FILENAME, 'a').close()
        open(canon_dir + '\\' + st.LOGS_FILENAME, 'a').close()
        open(canon_dir + '\\' + st.RULES_FILENAME, 'a').close()
        pref_dir = canon_dir + '\\' + "canon_prefs"
        os.makedirs(pref_dir)

        # For each member in the channel, make a file and add them to the proper role.
        members = val.client.get_all_members()
        for mem in members:
            player_pref = pref_dir + "\\" + mem.id
            with open(player_pref, "a") as fout:
                if gm[0] == mem.mention:
                    pref = {'user_type': UserType.gm.value, "recent_character": None}
                    await val.client.add_roles(mem, roles[2])
                else:
                    pref = {'user_type': UserType.observer.value, "recent_character": None}
                    await val.client.add_roles(mem, roles[0])
                json.dump(pref, fout, indent=1)
        status = st.INF_CANON_MADE
    else:
        status = st.ERR_CANON_EXISTS

    # If this doesn't already exists make channels.
    if status != st.ERR_CANON_EXISTS:
        # Prepare permission levels.
        n = discord.PermissionOverwrite(read_messages=False, send_messages=False)
        r = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        rw = discord.PermissionOverwrite(read_messages=True, send_messages=False)

        # Make category for the canon to reside in.
        category = await val.client.create_channel(m.server, canon[0], type=4)

        # Make channels for specific purposes per role.
        c = ["_IC", "_OOC", "_command_room", "_meta", "_gm_notes"]

        # IC Channel is locked on creation.
        room = await val.client.create_channel(m.server, canon[0] + c[0],
                                               (roles[0], r),
                                               (roles[1], r),
                                               (roles[2], r))
        await val.client.edit_channel(room, parent_id=category.id)

        # OOC Channel is open to all on creation.
        room = await val.client.create_channel(m.server, canon[0] + c[1],
                                               (roles[0], rw),
                                               (roles[1], rw),
                                               (roles[2], rw))
        await val.client.edit_channel(room, parent_id=category.id)

        # Command Room is open only to players and the gm.
        room = await val.client.create_channel(m.server, canon[0] + c[2],
                                               (roles[0], n),
                                               (roles[1], rw),
                                               (roles[2], rw))
        await val.client.edit_channel(room, parent_id=category.id)

        # Meta is for viewing the meta-rules of the canon only.
        room = await val.client.create_channel(m.server, canon[0] + c[3],
                                               (roles[0], r),
                                               (roles[1], r),
                                               (roles[2], r))
        await val.client.edit_channel(room, parent_id=category.id)

        # GM Notes is for the gm's eyes only.
        room = await val.client.create_channel(m.server, canon[0] + c[4],
                                               (roles[0], n),
                                               (roles[1], n),
                                               (roles[2], rw))
        await val.client.edit_channel(room, parent_id=category.id)

    return status


# Formatters #


async def format_alpha(m, command_info, array, expected_vars, log_op="<="):
    """A formatting helper method that makes sure that a string is only alphabetical."""
    # Read log_op as:  I expect the arguments to be <log_op> <expected_vars>.
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == val.escape_value:
            await s(m, st.ESCAPE)
            return val.escape_value

        # Check to make sure they didn't try to screw things up.
        if log_op == "<=" and len(array) > expected_vars:
            improperly_formatted = True
            await s(m, st.ERR_EXTRA_ARGS + str(expected_vars) + " or less. " + st.ERR_REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
            array = formatted_rsp.content.split(',')
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(m, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
            array = formatted_rsp.content.split(',')


        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(reg.non_alphabetic, '', array[j])

    return array


async def format_numer(m, command_info, array, expected_vars, log_op='<='):
    """A formatting helper method that makes sure that a string is only numeric."""
    # Read log_op as:  I expect the arguments to be <log_op> <expected_vars>.
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == val.escape_value:
            await s(m, st.ESCAPE)
            return val.escape_value

        # Check to make sure they didn't try to screw things up.
        if log_op == "<=" and len(array) > expected_vars:
            improperly_formatted = True
            await s(m, st.ERR_EXTRA_ARGS + str(expected_vars) + " or less. " + st.ERR_REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
            array = formatted_rsp.content.split(',')
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(m, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
            array = formatted_rsp.content.split(',')

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(reg.non_numeric, '', array[j])

    return array


async def format_none(m, command_info, array, expected_vars=1, log_op="<="):
    """A formatting helper method that makes sure that a set of values is only so many arguments."""
    # Read log_op as:  I expect the arguments to be <log_op> <expected_vars>.
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == val.escape_value:
            await s(m, st.ESCAPE)
            return val.escape_value

        single_statement = [""]

        # Concatenate if they had a comma. Basically, glue it back together. Elegiggle.
        if log_op == "<=" and len(array) > expected_vars:
            for bucket in len(array):
                single_statement[0] += bucket if bucket != len(array) - 1 else bucket + ','
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(m, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
            array = formatted_rsp.content.split(',')
        else:
            single_statement = array

    return single_statement


async def format_strip(m, command_info, array, expected_vars, log_op='<='):
    """A formatting helper method that makes sure that a string is only numeric."""
    # Read log_op as:  I expect the arguments to be <log_op> <expected_vars>.
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == val.escape_value:
            await s(m, st.ESCAPE)
            return val.escape_value

        # Check to make sure they didn't try to screw things up.
        if log_op == "<=" and len(array) > expected_vars:
            improperly_formatted = True
            await s(m, st.ERR_EXTRA_ARGS + str(expected_vars) + " or less. " + st.ERR_REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
            array = formatted_rsp.content.split(',')
        elif log_op == ">=" and len(array) < expected_vars:
            improperly_formatted = True
            await s(m, st.ERR_NOT_ENOUGH_ARGS + str(expected_vars) + ". Capiche? " + st.ERR_REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
            array = formatted_rsp.content.split(',')

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = array[j].strip()

    return array


# Utility #


def make_general_player_prefs():
    """Initializes the player prefs if they don't exist."""
    # TODO: Make generalized folder for general player-prefs
    # Make folder and initial docs
    prefs_dir = r"model\general\playerprefs"
    if not os.path.exists(prefs_dir):
        os.makedirs(prefs_dir)


def get_characters():
    """Returns an object with all character values in it."""
    # Pull JSON file for reading.
    with open(val.rel_canon + "\\" + st.CHARACTERS_FILENAME, "a") as fin:
        if os.stat(val.rel_canon + "\\" + st.CHARACTERS_FILENAME).st_size > 0:
            a = json.load(fin)
        else:
            a = {}

    return a


def redeem_alias(alias_i, aliases):
    """Returns the normalized form (first element in the list) of an alias value"""
    # Compare alias to other aliases
    for alias in aliases:
        for value in aliases[alias]:
            if value.lower() == alias_i.lower():
                return aliases[alias][0]
    return None


def get_mentionable_names():
    """Returns the pingable names of all players."""
    m_mentionable = []
    for mem in val.client.get_all_members():
        m_mentionable.append(mem.mention)

    return m_mentionable


def get_member_dict():
    """Returns a member dictionary linked to member.mention instances."""
    members = {}

    for mem in val.client.get_all_members():
        members[mem.mention] = mem

    return members


def players_exist(p_list):
    """Helper method to check to see if a set of players exist."""
    all_exist = True

    for p in p_list:
        if p not in get_mentionable_names():
            all_exist = False
            break

    return all_exist


def canon_exists(c_name):
    """Helper method to check to see if a specfic canon exists."""
    return os.path.exists("/model/canons/" + c_name)


def skill_roll_string(mod_r, mod_v, dice_pool, base_pool, purpose, norm_stat_types, stats, successes):
    """Formats a skill roll final string."""
    if len(mod_r) > 0:
        mod_s = "Modifiers: "
        for i in range(len(mod_r)):
            if i < len(mod_r) - 1:
                mod_s += mod_r[i] + " "
                mod_s += '(' + ('+' + mod_v[i] if int(mod_v[i]) > -1 else mod_v[i]) + "), "
            else:
                mod_s += mod_r[i] + " "
                mod_s += '(' + ('+' + mod_v[i] if int(mod_v[i]) > -1 else mod_v[i]) + ") "
    else:
        mod_s = "No Modifiers."

    if dice_pool > 0:
        pool_s = ("Base Pool: " + str(base_pool) + " ==> Dice Pool: " + str(dice_pool) if dice_pool != base_pool
                  else "Dice Pool: " + str(dice_pool))
    else:
        pool_s = "Luck Roll..."

    final_string = \
        "> " + purpose[0] + " (" + (norm_stat_types[0].title() if len(stats) == 1
                                    else norm_stat_types[0].title() + " + " + norm_stat_types[1].title()) + ")\n" \
        + "> " + mod_s + '\n' \
        + "> " + pool_s + '\n' \
        + "> " + successes

    return final_string


async def ask_for_mods(m):
    """Asks the user if they would like to add modifications to a roll."""
    # Define Lists
    mod_r = []  # Reasons
    mod_v = []  # Values

    # Ask for confirmation on modifiers.
    confirm = await user_input_against_aliases(m, st.ASK_IF_MODS, alias.CONFIRM_ALIASES,
                                               format_alpha, expected_vars=1)
    if confirm[0] == val.escape_value:
        return val.escape_value

    # Check confirm status.
    while confirm[0].lower() in alias.AFFIRM:
        # Request mod reason.
        reason = await request_of_user(m, st.REQ_MOD_REASON,
                                       format_none, expected_vars=1)
        if reason[0] == val.escape_value:
            return val.escape_value
        mod_r.append(reason[0])

        no_int = True  # No proper input yet given.

        while no_int:
            # Request mod amount.
            amount = await request_of_user(m, st.REQ_MOD_AMOUNT,
                                           format_numer, expected_vars=1)
            if amount[0] == val.escape_value:
                return val.escape_value
            no_int = not calc.is_int(amount[0])
            if no_int:
                await s(m, st.ERR_INV_FORM)

        mod_v.append(amount[0])

        # Ask if more mods.
        confirm = await user_input_against_aliases(m, st.ASK_IF_MORE_MODS, alias.CONFIRM_ALIASES,
                                                   format_alpha, expected_vars=1)
        if confirm[0] == val.escape_value:
            return val.escape_value

    return [mod_r, mod_v]


async def user_input_against_aliases(m, request_str, aliases, formatter, expected_vars):
    """Compares a set of aliases [a dictionary of lists] to a list of values"""
    # Prime the pump.
    i = 0
    used = []
    values = await request_of_user(m, request_str, formatter, expected_vars)
    if values[0] == val.escape_value:
        return val.escape_value

    # For each possible alias, check that the names the user input are valid.
    while i < len(values):
        invalid = True
        for name in aliases:
            for alias in aliases[name]:
                if alias.lower() == values[i].lower() and name not in used:  # Alias found & not used prev.
                    invalid = False
                    used.append(name)
                elif alias.lower() == values[i].lower() and name in used:  # Alias found & used prev.
                    # Inform the user that they've repeated an argument.
                    await s(m, st.ERR_REPEAT_ARG + values[i] + "!")
                    invalid = False

                    # Reprime the pump.
                    i = 0
                    used = []
                    values = await request_of_user(m, st.ERR_REPEAT, formatter, expected_vars)
                    if values[0] == val.escape_value:
                        return val.escape_value
                    break
            if not invalid:
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(m, st.ERR_INV_ARG + values[i] + "!")

            # Reprime the pump.
            i = 0
            used = []
            values = await request_of_user(m, st.ERR_REPEAT, formatter, expected_vars)
            if values[0] == val.escape_value:
                return val.escape_value

        else:  # Otherwise, alias found; continue.
            i += 1

    return values


async def user_input_against_list(m, request_str, comparators, formatter, expected_vars):
    """Compares a set of comparators to a list of values"""

    # Prime the pump.
    i = 0
    used = []
    values = await request_of_user(m, request_str, formatter, expected_vars)
    if values[0] == val.escape_value:
        return val.escape_value

    # For each possible alias, check that the names the user input are valid.
    while i < len(values):
        invalid = True
        for comparator in comparators:
            if comparator.lower() == values[i].lower() and comparator not in used:  # Alias found & not used prev.
                invalid = False
                used.append(comparator)
                i += 1
                break
            elif comparator.lower() == values[i].lower() and comparator in used:  # Alias found & used prev.
                # Inform the user that they've repeated an argument.
                await s(m, st.ERR_REPEAT_ARG + values[i] + "! " + st.ERR_REPEAT)
                invalid = False
                # Reprime the pump.
                i = 0
                used = []
                values = await request_of_user(m, request_str, formatter, expected_vars)
                if values[0] == val.escape_value:
                    return val.escape_value
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(m, st.ERR_INV_ARG + values[i] + "! " + st.ERR_REPEAT)
            # Reprime the pump.
            i = 0
            used = []
            values = await request_of_user(m, request_str, formatter, expected_vars)
            if values[0] == val.escape_value:
                return val.escape_value

    return values


async def wait_for_combat_affirmation(author, channel):
    """Method to encapsulate all parts of asking if someone is joining in a combat."""
    affirmed = None

    # TODO: Change request_of_user to hide more in this function.
    # It'll need to ask for author and channel.

    # Go until confirmation acquired.
    while not affirmed:
        affirmed = await val.client.wait_for_message(author=author, channel=channel)
        affirmed = affirmed.content
        if affirmed.lower() not in alias.AFFIRM and affirmed.lower() not in alias.DENY:
            affirmed = None
            await s(affirmed, st.ERR_NOT_YES_OR_NO)

    return affirmed


async def request_of_user(m, request_str, formatter, expected_vars, log_op="<="):
    """Ask a request for the user and return that request as a list of inputs or return an escape character."""
    await s(m, request_str)
    rsp = await val.client.wait_for_message(author=m.author, channel=m.channel)
    values = rsp.content.split(',')
    values = await formatter(m, rsp.content, values, expected_vars, log_op)
    if values[0] == val.escape_value:
        return val.escape_value
    return values


async def ask_for_user(m, request_str, expected_vars, log_op=">=", error=st.ERR_INV_FORM):
    """Speeds up asking for a player."""
    users = [""] # Dummy data to prime the pump.
    while not players_exist(users):
        users = await request_of_user(m, request_str, format_none, expected_vars=expected_vars, log_op=log_op)
        if users[0] == val.escape_value:
            return val.escape_value
        elif not players_exist(users):
            await s(m, error)

    return users


# Syntactical Candy #


def s(message, arg):
    """Syntactical candy:  sends a message."""
    return val.client.send_message(message.channel, arg)


def t(target, arg):
    """Syntactical candy:  sends a message to a location (typically a user)."""
    return val.client.send_message(target, arg)
