# ----------- Script by ReedRGale ----------- #
# Utility functions that lubricate the process of... a lot of things. #
# TODO: Separate this out further if you get the chance. Might be hell though.


# Import #

import json
import os
import re

from data import st, alias, reg, val
from output_func import calc


def get_actors():
    """Returns an object with all actor values in it."""
    # Make file if it doesn't exist.
    f = open("actors.txt", "a")
    f.close()

    # Pull JSON file for reading.
    with open("actors.txt", "r") as fin:
        if os.stat("actors.txt").st_size > 0:
            a = json.load(fin)
        else:
            a = {}

    return a


async def add_actor(message):
    """A function to store a JSON entry of a character"""
    # Ask for stat values.
    for field in val.focused_actor:

        input_not_recorded = True

        # Loop to not have to repeat the command over and over if an input is wrong.
        while input_not_recorded:

            # Ask user for each field.
            await s(message, st.REQ_ACTOR + field + " value:")
            stat_rsp = await val.client.wait_for_message(author=message.author)

            # Escape command early.
            if stat_rsp.content == val.escape_value:
                return val.escape_value

            # List of checks to make sure their input makes sense.
            elif field != "NAME" and calc.is_int(stat_rsp.content):
                stat_val = int(stat_rsp.content)
                non_neg = stat_val > -1
                lt_fift = stat_val < 15

                # Inform the user that -1 or less might be a bit low.
                if not non_neg:
                    await s(message, st.LT_ZERO)

                # Inform the user that 16 or more is too high.
                if not lt_fift:
                    await s(message, st.GT_FIFT)

                # User got it right, make sure to break this loop.
                if non_neg and lt_fift:
                    val.focused_actor[field] = stat_rsp.content
                    input_not_recorded = False

            elif field == "NAME":
                # Store the name of the character.
                val.focused_actor[field] = stat_rsp.content
                input_not_recorded = False

            elif field != "NAME" and not calc.is_int(stat_rsp.content):
                await s(message, st.INV_FORM)

    # Make file if it doesn't exist.
    f = open("actors.txt", "a")
    f.close()

    # Pull JSON file for updating.
    with open("actors.txt", "r") as fin:
        if os.stat("actors.txt").st_size > 0:
            actors = json.load(fin)
        else:
            actors = {}

    # TODO: Make sure you can't write over characters unless you're the GM.

    # Append actor to file.
    actors[val.focused_actor["NAME"]] = val.focused_actor

    # Update character file.
    with open("actors.txt", "w") as fout:
        json.dump(actors, fout, indent=1)


def redeem_alias(alias_i, aliases):
    """Returns the normalized form (first element in the list) of an alias value"""
    # Compare alias to other aliases
    for alias in aliases:
        for value in aliases[alias]:
            if value.lower() == alias_i.lower():
                return aliases[alias][0]

    return None


async def user_input_against_aliases(message, request_str, aliases, formatter, expected_vars):
    """Compares a set of aliases [a dictionary of lists] to a list of values"""
    # Prime the pump.
    i = 0
    used = []
    values = await request_of_user(message, request_str, formatter, expected_vars)
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
                    await s(message, st.REPEAT_ARG + values[i] + "!")
                    invalid = False

                    # Reprime the pump.
                    i = 0
                    used = []
                    values = await request_of_user(message, st.REPEAT, formatter, expected_vars)
                    if values[0] == val.escape_value:
                        return val.escape_value
                    break
            if not invalid:
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(message, st.INV_ARG + values[i] + "!")

            # Reprime the pump.
            i = 0
            used = []
            values = await request_of_user(message, st.REPEAT, formatter, expected_vars)
            if values[0] == val.escape_value:
                return val.escape_value

        else:  # Otherwise, alias found; continue.
            i += 1

    return values


async def user_input_against_list(message, request_str, comparators, formatter, expected_vars):
    """Compares a set of comparators to a list of values"""

    # Prime the pump.
    i = 0
    used = []
    values = await request_of_user(message, request_str, formatter, expected_vars)
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
                await s(message, st.REPEAT_ARG + values[i] + "! " + st.REPEAT)
                invalid = False
                # Reprime the pump.
                i = 0
                used = []
                values = await request_of_user(message, request_str, formatter, expected_vars)
                if values[0] == val.escape_value:
                    return val.escape_value
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(message, st.INV_ARG + values[i] + "! " + st.REPEAT)
            # Reprime the pump.
            i = 0
            used = []
            values = await request_of_user(message, request_str, formatter, expected_vars)
            if values[0] == val.escape_value:
                return val.escape_value

    return values


async def format_alpha(message, command_info, array, expected_vars):
    """A formatting helper method that makes sure that a string is only alphabetical."""
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == val.escape_value:
            await s(message, st.ESCAPE)
            return val.escape_value

        # Check to make sure they didn't try to screw things up.
        if len(array) > expected_vars:
            improperly_formatted = True
            await s(message, st.EXTRA_ARGS + str(expected_vars) + " or less. " + st.REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=message.author, channel=message.channel)
            array = formatted_rsp.content.split(',')

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(reg.non_alphabetic, '', array[j])

    return array


async def format_numer(message, command_info, array, expected_vars):
    """A formatting helper method that makes sure that a string is only numeric."""
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == val.escape_value:
            await s(message, st.ESCAPE)
            return val.escape_value

        # Check to make sure they didn't try to screw things up.
        if len(array) > expected_vars:
            improperly_formatted = True
            await s(message, st.EXTRA_ARGS + str(expected_vars) + " or less. " + st.REPEAT)
            formatted_rsp = await val.client.wait_for_message(author=message.author, channel=message.channel)
            array = formatted_rsp.content.split(',')

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(reg.non_numeric, '', array[j])

    return array


async def format_none(message, command_info, array, expected_vars=1):
    """A formatting helper method that makes sure that a ser of values is only so many arguments."""
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == val.escape_value:
            await s(message, st.ESCAPE)
            return val.escape_value

        single_statement = [""]

        # Concatenate if they had a comma. Basically, glue it back together. Elegiggle.
        if len(array) > expected_vars:
            for bucket in len(array):
                single_statement[0] += bucket if bucket == len(array) else bucket + ','
        else:
            single_statement = array

    return single_statement


async def request_of_user(message, request_str, formatter, expected_vars):
    """Ask a request for the user and return that request as a list of inputs or return an escape character."""
    await s(message, request_str)
    rsp = await val.client.wait_for_message(author=message.author, channel=message.channel)
    values = rsp.content.split(',')
    values = await formatter(message, rsp.content, values, expected_vars)
    if values[0] == val.escape_value:
        return val.escape_value
    return values


async def perform_skill_roll(message):
    """Performs a basic skill roll."""
    # Request roll purpose.
    purpose = await request_of_user(message, st.REQ_ROLL_PURPOSE,
                                    format_none, expected_vars=1)
    if purpose[0] == val.escape_value:
        return val.escape_value

    # Find the related character.
    actors_json = get_actors()
    all_names = []
    for name in actors_json:
        all_names.append(name)
    actors = await user_input_against_list(message, st.REQ_ACTIVE_ACTOR, all_names,
                                           format_alpha, expected_vars=1)
    if actors[0] == val.escape_value:
        return val.escape_value

    # Request stats for roll.
    stats = await user_input_against_aliases(message, st.REQ_STATS, alias.STATS_ALIASES,
                                             format_alpha, expected_vars=2)
    if stats[0] == val.escape_value:
        return val.escape_value

    # Ensure we have the correct json object.
    actors_json = actors_json[actors[0].title()]

    # Retrieve mods.
    mod = await ask_for_mods(message)
    if actors[0] == val.escape_value:
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
        dice_pool += int(actors_json[stat])

    base_pool = dice_pool

    for mod in mod_v:
        dice_pool += int(mod)

    # Roll the die and make the string.
    successes = calc.skill_roll(dice_pool)
    final_string = skill_roll_string(mod_r, mod_v, dice_pool, base_pool, purpose,
                                     norm_stat_types, stats, successes)

    return final_string


async def ask_for_mods(message):
    """Asks the user if they would like to add modifications to a roll."""
    # Define Lists
    mod_r = []  # Reasons
    mod_v = []  # Values

    # Ask for confirmation on modifiers.
    confirm = await user_input_against_aliases(message, st.ASK_IF_MODS, alias.CONFIRM_ALIASES,
                                               format_alpha, expected_vars=1)
    if confirm[0] == val.escape_value:
        return val.escape_value

    # Check confirm status.
    while confirm[0].lower() in alias.AFFIRM:
        # Request mod reason.
        reason = await request_of_user(message, st.REQ_MOD_REASON,
                                       format_none, expected_vars=1)
        if reason[0] == val.escape_value:
            return val.escape_value
        mod_r.append(reason[0])

        no_int = True  # No proper input yet given.

        while no_int:
            # Request mod amount.
            amount = await request_of_user(message, st.REQ_MOD_AMOUNT,
                                           format_numer, expected_vars=1)
            if amount[0] == val.escape_value:
                return val.escape_value
            no_int = not calc.is_int(amount[0])
            if no_int:
                await s(message, st.INV_FORM)

        mod_v.append(amount[0])

        # Ask if more mods.
        confirm = await user_input_against_aliases(message, st.ASK_IF_MORE_MODS, alias.CONFIRM_ALIASES,
                                                   format_alpha, expected_vars=1)
        if confirm[0] == val.escape_value:
            return val.escape_value

    return [mod_r, mod_v]


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


# Syntactical Candy #


def s(message, arg):
    """Syntactical candy:  sends a message."""
    return val.client.send_message(message.channel, arg)
