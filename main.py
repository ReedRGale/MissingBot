# ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #

# Import #

import json
import random
import re
import math
import discord
import asyncio


# Global Constants #


SUCCESS_VALUES = 4
FAILURE_VALUES = 6
DICE_SIZE = 10
SUCCESS = 'S - '
FAILURE = 'F - '
AGAIN = 'A - '
NEW_LINE = '\n'

# Global Vars #


client = discord.Client()
app_token = "MzUzMTEzODg4Nzg0NjQ2MTQ0.DIunqw.tTJF2f3cDXSYXOcMdXMCETDqrLA"


# Error Messages #


extra_args = "It appears you attempted to use more than the required args. This command wants "


# Regexes #


nonnumeric = '[^0-9]'


# Events #


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):

    # !forecast:  Prints out success value.
    fc = "!forecast"
    db = "!debug"

    if message.content.startswith(fc):
        # Format: [dice_pool, forecast_successes]
        args = message.content.split(',')

        # Check to make sure they didn't try to screw things up.
        if len(args) > 3:
            return await client.send_message(message.channel, extra_args + '2')

        # Filter out non-numeric data
        for i in range(0, 2):
            args[i] = re.sub(nonnumeric, '', args[i])

        return await client.send_message(message.channel, percent(calc_success(int(args[0]), int(args[1]))))

    if message.content.startswith(db):
        # Format: <relative>
        args = message.content.split(',')

        # Check to make sure they didn't try to screw things up.
        if len(args) > 3:
            return await client.send_message(message.channel, extra_args + '2')

        # Filter out non-numeric data
        for i in range(0, 2):
            args[i] = re.sub(nonnumeric, '', args[i])

        return await client.send_message(message.channel, branching_module(int(args[0]), int(args[1]), int(args[1])))

    # TODO: Make help command.

# Methods #


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
