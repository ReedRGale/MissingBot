# ----------- Script by ReedRGale ----------- #
# Mathematical functions that lubricate the process of mathing #


# Imports #


import math
import random

from model import st, val


# Helper Functions #


def calc_success(dice_pool, success_forecast):
    """Returns the likelihood of success for a given pool of dice and expected number of successes"""

    return (math.pow(val.SUCCESS_VALUES, success_forecast)
            * math.pow(val.FAILURE_VALUES, (dice_pool - success_forecast))
            * combination(dice_pool, success_forecast)
            / math.pow(val.DICE_SIZE, dice_pool))


def percent(num):
    """Converts a number into a percentage"""
    percent_val = num * 100
    percent_str = str(percent_val) + '%'
    return percent_str


def combination(dice_pool, success_forecast):
    """Returns the combinitorics definition of a combination"""
    return (factorial(dice_pool)
            / (factorial(success_forecast)
            * factorial(dice_pool - success_forecast)))


def factorial(num):
    """Returns the factorial"""
    return num * factorial(num - 1) if num - 1 > 0 else 1


def branching_module(dice_pool, successes, forecast, ten_agains=0, succ_set=[]):
    """Helper Function for me to simulate the branching properties of ten again"""
    # String to represent the simulation...
    branches = ''

    # If first call (tens == 0), simulate normal dice roll.
    if ten_agains == 0:
        # This would represent solving the problem normally.
        for _ in range(successes):
            branches += st.SUCCESS
        for _ in range(dice_pool - successes):
            branches += st.FAILURE
        branches = branches[:-2] + '\n'

    # <Under what circumstances does it recurse?> #

    # If there's a ten-again set to resolve...
    if ten_agains > 0:

        # Track number of successes for recursive purposes.
        succ_set.append(successes)
        succ_set.append(ten_agains)

        for _ in range(ten_agains):
            branches += st.AGAIN
        for _ in range(successes):
            branches += st.SUCCESS
        for _ in range(dice_pool - successes - ten_agains):
            branches += st.FAILURE
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


def skill_roll(dice_pool):
    """Rolls a stat-based skill roll"""
    # Prepare initial success.
    successes = 0

    if dice_pool > 0:
        for _ in range(dice_pool):
            num = roll_die()

            while num == val.DICE_SIZE:
                successes += 1
                num = roll_die()

            if num > val.FAILURE_VALUES:
                successes += 1
        successes = "Successes: " + str(successes)
    else:
        num = roll_die()

        if num != 1:
            while num == val.DICE_SIZE:
                successes += 1
                num = roll_die()
            successes = "Successes: " + str(successes)
        else:
            successes = "CRITICAL FAILURE"

    return successes


def roll_die():
    """Roll a 10 sided die."""
    return random.randint(1, val.DICE_SIZE)


def is_int(num):
    """Tool to tell me if something is an int or not without crashing."""
    try:
        int(num)
        return True
    except ValueError:
        return False
