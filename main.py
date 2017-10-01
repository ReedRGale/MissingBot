# ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #

# Import #

import json
import random
import re
import os
import math
import discord
import asyncio


# Global Constants #


AFFIRM = ["y", "yes", "yup", "uhuh", "ye", "yea"]
DENY = ["n", "no", "nah", "nope", "nu", "nuu", "nuuu", "nuuuu", "nuuuuu", "nuuuuuu", "nuuuuuuu", "nuuuuuuuu",
        "noo", "nooo", "noooo", "nooooo", "nooooooo", "noooooooo"]
CONFIRM_ALIASES = {"AFFIRM": AFFIRM, "DENY": DENY}

ATH = ["ATHLETICS", "ATH"]
DEX = ["DEXTERITY", "DEX"]
CHR = ["CHARISMA", "CHR"]
ACA = ["ACADEMICS", "ACA"]
SAV = ["SAVVY", "SAV"]
STATS_ALIASES = {"ATH": ATH, "DEX": DEX, "CHR": CHR, "ACA":  ACA, "SAV": SAV}

REQ_STATS = "Which stats are related to this roll? Separate with commas. \n"
REQ_ACTIVE_ACTOR = "Which character is rolling? \n"
REQ_ACTOR = "Please provide a "
REQ_MOD_REASON = "What's one factor affecting this roll?"
REQ_MOD_AMOUNT = "What's by how many dice should this affect the roll? (i.e. -3, 4, 1, 2, etc...)"
ASK_IF_MODS = "Are there modifications to this roll? " \
             "(i.e. Its dark; You made a torch to light the way; etc...)"
ASK_IF_MORE = "Any more?"
SAVED = "Databank updated, for whatever reason it needed updating!"

SUCCESS_VALUES = 4
FAILURE_VALUES = 6
DICE_SIZE = 10
SUCCESS = 'S - '
FAILURE = 'F - '
AGAIN = 'A - '
NEW_LINE = '\n'


# Global Vars #


escape_value = '!'  # TODO: change this value and see if it still works.
focused_actor = {"NAME": "", "ATHLETICS": 0, "DEXTERITY": 0, "CHARISMA": 0, "ACADEMICS":  0, "SAVVY": 0}
client = discord.Client()
app_token = "MzUzMTEzODg4Nzg0NjQ2MTQ0.DIunqw.tTJF2f3cDXSYXOcMdXMCETDqrLA"


# Error Messages #


EXTRA_ARGS = "It appears you attempted to use more than the required args. This command wants "
INV_ARG = "I don't recognize the keyword "
REPEAT_ARG = "You've already used the keyword "
INV_FORM = "It seems invalid. Try again."
LT_ZERO = "A stat can't be less than 0. And, let's be fair, do you really want it to be?"
GT_FIFT = "A stat can't be greater than 15. And that's already obnoxiously high as it is."
REPEAT = "Could you repeat the command?"
ESCAPE = "Escaping command..."


# Regexes #


non_numeric = '[^\d\-]'
non_alphabetic = '[^a-zA-Z]'


# Events #


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):

    # List of commands.
    fc = "!forecast"
    nr = "!newactor"
    lr = "!listactors"
    sl = "!skillroll"
    hp = "!help"
    db = "!debug"
    commands = [fc, nr, lr, sl, hp, db]

    # # # # # # !forecast command # # # # # #

    if message.content.startswith(fc):
        # Format: [dice_pool, forecast_successes]
        args = message.content.split(',')

        # Check to make sure they didn't try to screw things up.
        if len(args) > 3:
            return await s(message, EXTRA_ARGS + '2')

        # Filter out non-numeric data
        for i in range(0, 2):
            args[i] = re.sub(non_numeric, '', args[i])

        return await s(message, percent(calc_success(int(args[0]), int(args[1]))))

    # # # # # # !newactor command # # # # # #

    if message.content.startswith(nr):
        # Format: <Type Command>

        # Ask for stat values.
        for field in focused_actor:

            input_not_recorded = True

            # Loop to not have to repeat the command over and over if an input is wrong.
            while input_not_recorded:

                # Ask user for the actor's field.
                await s(message, REQ_ACTOR + field + " value:")
                stat_rsp = await client.wait_for_message(author=message.author)

                # Escape command early.
                if stat_rsp.content == escape_value:
                    await s(message, ESCAPE)
                    return

                # List of checks to make sure their input makes sense.
                elif field != "NAME" and is_int(stat_rsp.content):
                    stat_val = int(stat_rsp.content)
                    non_neg = stat_val > -1
                    lt_fift = stat_val < 15

                    # Inform the user that -1 or less might be a bit low.
                    if not non_neg:
                        await s(message, LT_ZERO)

                    # Inform the user that 16 or more is too high.
                    if not lt_fift:
                        await s(message, GT_FIFT)

                    # User got it right, make sure to break this loop.
                    if non_neg and lt_fift:
                        focused_actor[field] = stat_rsp.content
                        input_not_recorded = False

                elif field == "NAME":
                    # Store the name of the character.
                    focused_actor[field] = stat_rsp.content
                    input_not_recorded = False

                elif field != "NAME" and not is_int(stat_rsp.content):
                    await s(message, INV_FORM)

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
        actors[focused_actor["NAME"]] = focused_actor

        # Update character file.
        with open("actors.txt", "w") as fout:
            json.dump(actors, fout, indent=1)

        return await s(message, SAVED)

    # # # # # # !listactors command # # # # # #

    if message.content.startswith(lr):
        # Format: <Type Command>

        # Load in file.
        actors = get_actors()

        # Concatenate all names.
        all_names = "Character Names: \n"

        for name in actors:
            all_names += '► ' + name + '\n'

        return await s(message, all_names)

    # # # # # # !skillroll command # # # # # #

    if message.content.startswith(sl):
        # Format: <Type Command>

        # TODO: Ask for reason for roll

        # Make sure that values are acceptable
        stats = await user_input_against_aliases(message, REQ_STATS, STATS_ALIASES, format_alpha, expected_vars=2)
        if stats[0] == escape_value:
            return

        # Find the related character.
        actors_json = get_actors()
        all_names = []
        for name in actors_json:
            all_names.append(name)
        actors = await user_input_against_list(message, REQ_ACTIVE_ACTOR, all_names, format_alpha, expected_vars=1)
        if actors[0] == escape_value:
            return

        # Ask for confirmation on modifiers.
        confirm = await user_input_against_aliases(message, ASK_IF_MODS, CONFIRM_ALIASES, format_alpha, expected_vars=1)
        if confirm[0] == escape_value:
            return

        # Define Lists
        mod_r = []  # Reasons
        mod_v = []  # Values

        # Check confirm status.
        while confirm[0].lower() in AFFIRM:
            # Request mod reason.
            reason = await request_of_user(message, REQ_MOD_REASON, format_none, expected_vars=1)
            if reason[0] == escape_value:
                return escape_value
            mod_r.append(reason[0])

            no_int = True  # No proper input yet given.

            while no_int:
                # Request mod amount.
                amount = await request_of_user(message, REQ_MOD_AMOUNT, format_numer, expected_vars=1)
                if amount[0] == escape_value:
                    return escape_value
                no_int = not is_int(amount[0])
                if no_int:
                    await s(message, INV_FORM)

            mod_v.append(amount[0])

            # Ask if more mods.
            confirm = await user_input_against_aliases(message, ASK_IF_MORE, CONFIRM_ALIASES,
                                                       format_alpha, expected_vars=1)
            if confirm[0] == escape_value:
                return

        # TODO: Complete the roll.

        # TODO: Format the roll string.

        return await client.send_message(message.channel, actors_json)

    # # # # # # !help command # # # # # #

    if message.content.startswith(hp):

        all_commands = "Commands are currently as follows: \n\n"

        for command in commands:
            all_commands += command + '\n'

        # TODO: Add support for explaining what commands do.

        return await s(message, all_commands)

    # # # # # # !debug command # # # # # #

    if message.content.startswith(db):
        # Format: <relative>
        test = await request_of_user(message, "TESTING REGEX", format_numer, expected_vars=1)
        return await client.send_message(message.channel, test[0])


# Methods #


async def user_input_against_aliases(message, request_str, aliases, formatter, expected_vars):
    """Compares a set of aliases [a dictionary of lists] to a list of values"""
    # Prime the pump.
    i = 0
    used = []
    values = await request_of_user(message, request_str, formatter, expected_vars)
    if values[0] == escape_value:
        return escape_value

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
                    await s(message, REPEAT_ARG + values[i] + "!")
                    invalid = False

                    # Reprime the pump.
                    i = 0
                    used = []
                    values = await request_of_user(message, REPEAT, formatter, expected_vars)
                    if values[0] == escape_value:
                        return escape_value
                    break
            if not invalid:
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(message, INV_ARG + values[i] + "!")

            # Reprime the pump.
            i = 0
            used = []
            values = await request_of_user(message, REPEAT, formatter, expected_vars)
            if values[0] == escape_value:
                return escape_value

        else:  # Otherwise, alias found; continue.
            i += 1

    return values


async def user_input_against_list(message, request_str, comparators, formatter, expected_vars):
    """Compares a set of comparators to a list of values"""

    # Prime the pump.
    i = 0
    used = []
    values = await request_of_user(message, request_str, formatter, expected_vars)
    if values[0] == escape_value:
        return escape_value

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
                await s(message, REPEAT_ARG + values[i] + "! " + REPEAT)
                invalid = False
                # Reprime the pump.
                i = 0
                used = []
                values = await request_of_user(message, request_str, formatter, expected_vars)
                if values[0] == escape_value:
                    return escape_value
                break
        if invalid:  # Alias unfound.
            # Inform the user that their argument is invalid.
            await s(message, INV_ARG + values[i] + "! " + REPEAT)
            # Reprime the pump.
            i = 0
            used = []
            values = await request_of_user(message, request_str, formatter, expected_vars)
            if values[0] == escape_value:
                return escape_value

    return values


async def format_alpha(message, command_info, array, expected_vars):
    """A formatting helper method that makes sure that a string is only alphabetical."""
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == escape_value:
            await s(message, ESCAPE)
            return escape_value

        # Check to make sure they didn't try to screw things up.
        if len(array) > expected_vars:
            improperly_formatted = True
            await s(message, EXTRA_ARGS + str(expected_vars) + " or less. " + REPEAT)
            formatted_rsp = await client.wait_for_message(author=message.author, channel=message.channel)
            array = formatted_rsp.content.split(',')

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(non_alphabetic, '', array[j])

    return array


async def format_numer(message, command_info, array, expected_vars):
    """A formatting helper method that makes sure that a string is only alphabetical."""
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == escape_value:
            await s(message, ESCAPE)
            return escape_value

        # Check to make sure they didn't try to screw things up.
        if len(array) > expected_vars:
            improperly_formatted = True
            await s(message, EXTRA_ARGS + str(expected_vars) + " or less. " + REPEAT)
            formatted_rsp = await client.wait_for_message(author=message.author, channel=message.channel)
            array = formatted_rsp.content.split(',')

        # Filter out non-alphabetic data
        for j in range(len(array)):
            array[j] = re.sub(non_numeric, '', array[j])

    return array


async def format_none(message, command_info, array, expected_vars):
    """A formatting helper method that makes sure that a ser of values is only so many arguments."""
    improperly_formatted = True

    while improperly_formatted:
        # Assume properly formatted until otherwise noted.
        improperly_formatted = False

        # Escape command early.
        if command_info == escape_value:
            await s(message, ESCAPE)
            return escape_value

        # Check to make sure they didn't try to screw things up.
        if len(array) > expected_vars:
            improperly_formatted = True
            await s(message, EXTRA_ARGS + str(expected_vars) + " or less. " + REPEAT)
            formatted_rsp = await client.wait_for_message(author=message.author, channel=message.channel)
            array = formatted_rsp.content.split(',')

    return array


async def request_of_user(message, request_str, formatter, expected_vars):
    """Ask a request for the user and return that request as a list of inputs or return an escape character."""
    await s(message, request_str)
    rsp = await client.wait_for_message(author=message.author, channel=message.channel)
    values = rsp.content.split(',')
    values = await formatter(message, rsp.content, values, expected_vars)
    if values[0] == escape_value:
        return escape_value
    return values


def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def s(message, arg):
    """Syntactical candy:  sends a message."""
    return client.send_message(message.channel, arg)


def get_actors():
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


def calc_success(dice_pool, success_forecast):
    """Returns the likelihood of success for a given pool of dice and expected number of successes"""

    # TODO: Account for '10 Again' rule

    return (math.pow(SUCCESS_VALUES, success_forecast)
           * math.pow(FAILURE_VALUES, (dice_pool - success_forecast))
           * combination(dice_pool, success_forecast)
           / math.pow(DICE_SIZE, dice_pool))


def percent(val):
    """Converts a number into a percentage"""
    percent_val = val * 100
    percent_str = str(percent_val) + '%'
    return percent_str


def combination(dice_pool, success_forecast):
    """Returns the combinitorics definition of a combination"""
    return (factorial(dice_pool)
            / (factorial(success_forecast)
            * factorial(dice_pool - success_forecast)))


def factorial(value):
    """Returns the factorial"""
    return value * factorial(value - 1) if value - 1 > 0 else 1


def branching_module(dice_pool, successes, forecast, ten_agains=0, succ_set=[]):
    """Helper Function for me to simulate the branching properties of ten again"""
    # String to represent the simulation...
    branches = ''

    # If first call (tens == 0), simulate normal dice roll.
    if ten_agains == 0:
        # This would represent solving the problem normally.
        for _ in range(successes):
            branches += SUCCESS
        for _ in range(dice_pool - successes):
            branches += FAILURE
        branches = branches[:-2] + NEW_LINE

    # <Under what circumstances does it recurse?> #

    # If there's a ten-again set to resolve...
    if ten_agains > 0:

        # Track number of successes for recursive purposes.
        succ_set.append(successes)
        succ_set.append(ten_agains)

        for _ in range(ten_agains):
            branches += AGAIN
        for _ in range(successes):
            branches += SUCCESS
        for _ in range(dice_pool - successes - ten_agains):
            branches += FAILURE
        branches = branches[:-2]

        if forecast != sum(succ_set):
            # What conditions does this need to meet?
            # > The dice pool is now the number of ten-agains.
            # > The successes are complicated.
            # > > If I'm at ten-agains == dice_pool, then successes must be 0
            # > Ten-agains should reset at 0 unless...
            # > > If sum(success_set) + 1 != forecast, then ten-agains need to == 0
            branches += " : " + branching_module(ten_agains,
                                                 ten_agains if forecast == sum(succ_set) + ten_agains else 0,
                                                 forecast,
                                                 1,
                                                 succ_set)

        # What's our stopping condition:  Hitting a single success roll.

    # If there's still more ten-agains to resolve...
    if ten_agains < math.floor(successes / 2):
        # What conditions does this need to meet?
        # > The dice pool is the same.
        # > The successes are now down by two. This is because...
        # > > The ten-again accounts for at least 1 success.
        # > > If we were to include the ten-again in successes, we wouldn't properly decouple the new set.
        # > > Accounting for one more success: If we don't use the ten-again property, there's no point representing it.
        # > The ten-agains must increase to encompass all useful possibilities.
        branches += branching_module(dice_pool,
                                     successes - (ten_agains + 2),
                                     forecast,
                                     ten_agains + 1,
                                     succ_set)

    return branches


def add_actor(name, ath, dex, chr, acd, sav):
    """A function to store a JSON entry of a character"""


def skill_check(first, second, actor, **mods):
    """A function that takes skill types, character and mods, rolls that many die, then returns a formatted string."""
    # TODO: Find a way to store characters.


def skill_calc(*mods):
    """A function that takes two skill values and modifiers, adds them together, then rolls that many die."""
    succ = 0;
    pool = 0;

    # Add all mods together.
    for mod in mods:
        pool += mod

    # Roll the proper number of die.
    for _ in range(pool):
        val = roll_die()

        while val == DICE_SIZE:
            succ += 1
            val = roll_die()

        if val > FAILURE_VALUES:
            succ += 1

    return succ


def roll_die():
    return random.randint(1, DICE_SIZE)


# Code #


client.run(app_token)
