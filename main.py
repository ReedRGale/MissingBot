# ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #


# TODO: Figure out what to decouple.
# TODO: Figure out how to use inline to make more usable interfaces.


# Import #

import calc
import alias
import st
import reg
import val
import util

import re


# Events #


@val.client.event
async def on_ready():
    print('Logged in as')
    print(val.client.user.name)
    print(val.client.user.id)
    print('------')


@val.client.event
async def on_message(message):

    # List of commands.
    # TODO: !update to update an entry.
    fc = "forecast"
    nr = "newactor"
    lr = "listactors"
    sl = "skillroll"
    hp = "help"
    db = "debug"
    commands = [fc, nr, lr, sl, hp, db]

    # # # # # # !forecast command # # # # # #

    if message.content.startswith('!' + fc):
        # Format: [dice_pool, forecast_successes]

        # TODO: Update to ask this in separated questions.

        args = message.content.split(',')

        # Check to make sure they didn't try to screw things up.
        if len(args) > 3:
            return await s(message, st.EXTRA_ARGS + '2')

        # Filter out non-numeric data
        for i in range(0, 2):
            args[i] = re.sub(reg.non_numeric, '', args[i])

        return await s(message, calc.percent(calc.calc_success(int(args[0]), int(args[1]))))

    # # # # # # !newactor command # # # # # #

    if message.content.startswith('!' + nr):

        # Ask the questions and add the actor.
        await util.add_actor(message)
        return await s(message, st.SAVED)

    # # # # # # !listactors command # # # # # #

    if message.content.startswith('!' + lr):

        # Load in file.
        actors = util.get_actors()

        # Concatenate all names.
        all_names = "Character Names: \n"

        for name in actors:
            all_names += '► ' + name + '\n'

        return await s(message, all_names)

    # # # # # # !skillroll command # # # # # #

    if message.content.startswith('!' + sl):
        # Format: <Type Command>
        # TODO: Snip out parts of this for readability.

        # Request roll purpose.
        purpose = await util.request_of_user(message, st.REQ_ROLL_PURPOSE,
                                             util.format_none, expected_vars=1)
        if purpose[0] == val.escape_value:
            return val.escape_value

        # Make sure that values are acceptable
        stats = await util.user_input_against_aliases(message, st.REQ_STATS, alias.STATS_ALIASES,
                                                      util.format_alpha, expected_vars=2)
        if stats[0] == val.escape_value:
            return

        # Find the related character.
        actors_json = util.get_actors()
        all_names = []
        for name in actors_json:
            all_names.append(name)
        actors = await util.user_input_against_list(message, st.REQ_ACTIVE_ACTOR, all_names,
                                                    util.format_alpha, expected_vars=1)
        if actors[0] == val.escape_value:
            return

        # Ensure we have the correct json object.
        actors_json = actors_json[actors[0].title()]

        # Ask for confirmation on modifiers.
        confirm = await util.user_input_against_aliases(message, st.ASK_IF_MODS, alias.CONFIRM_ALIASES,
                                                        util.format_alpha, expected_vars=1)
        if confirm[0] == val.escape_value:
            return

        # Define Lists
        mod_r = []  # Reasons
        mod_v = []  # Values

        # Check confirm status.
        while confirm[0].lower() in alias.AFFIRM:
            # Request mod reason.
            reason = await util.request_of_user(message, st.REQ_MOD_REASON,
                                                util.format_none, expected_vars=1)
            if reason[0] == val.escape_value:
                return val.escape_value
            mod_r.append(reason[0])

            no_int = True  # No proper input yet given.

            while no_int:
                # Request mod amount.
                amount = await util.request_of_user(message, st.REQ_MOD_AMOUNT,
                                                    util.format_numer, expected_vars=1)
                if amount[0] == val.escape_value:
                    return val.escape_value
                no_int = not calc.is_int(amount[0])
                if no_int:
                    await s(message, st.INV_FORM)

            mod_v.append(amount[0])

            # Ask if more mods.
            confirm = await util.user_input_against_aliases(message, st.ASK_IF_MORE_MODS, alias.CONFIRM_ALIASES,
                                                            util.format_alpha, expected_vars=1)
            if confirm[0] == val.escape_value:
                return

        # Complete the roll.
        norm_stat_types = []
        base_pool = 0
        dice_pool = 0
        successes = 0

        for stat in stats:
            norm_stat_types.append(util.redeem_alias(stat, alias.STATS_ALIASES))

        for stat in norm_stat_types:
            dice_pool += int(actors_json[stat])

        base_pool = dice_pool

        for mod in mod_v:
            dice_pool += int(mod)

        # Roll the proper number of die.
        if dice_pool > 0:
            for _ in range(dice_pool):
                num = calc.roll_die()

                while num == val.DICE_SIZE:
                    successes += 1
                    num = calc.roll_die()

                if num > val.FAILURE_VALUES:
                    successes += 1
            successes = "Successes: " + str(successes)
        else:
            num = calc.roll_die()

            if num != 1:
                while num == val.DICE_SIZE:
                    successes += 1
                    num = calc.roll_die()
                successes = "Successes: " + str(successes)
            else:
                successes = "CRITICAL FAILURE"

        # Put together mod string.
        if len(mod_r) > 0:
            mod_s = "Modifiers: "
            for i in range(len(mod_r)):
                if i < len(mod_r):
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

        final_string =  \
            "> " + purpose[0] + " (" + (norm_stat_types[0].title() if len(stats) == 1
                                        else norm_stat_types[0].title() + " + " + norm_stat_types[1].title()) + ")\n" \
            + "> " + mod_s + '\n' \
            + "> " + pool_s + '\n' \
            + "> " + successes

        return await s(message, final_string)

    # # # # # # !help command # # # # # #

    if message.content.startswith('!' + hp):

        help_message = "Commands are currently as follows: \n\n"

        if fc in message.content:
            help_message = st.FC_HELP
        elif nr in message.content:
            help_message = st.NR_HELP
        elif lr in message.content:
            help_message = st.LR_HELP
        elif sl in message.content:
            help_message = st.SL_HELP
        elif db in message.content:
            help_message = st.DB_HELP
        else:
            for command in commands:
                help_message += command + '\n'
            help_message += "For more information use !help followed by a command to get more information." \
                            "i.e. !help help."

        return await s(message, help_message)

    # # # # # # !debug command # # # # # #

    if message.content.startswith('!' + db):
        # Format: <relative>

        # TODO: Test edit_message
        # TODO: Test on_reaction
        # TODO: Test create_channel

        test = await util.request_of_user(message, "TESTING REGEX", util.format_numer, expected_vars=1)
        return await s(message, test[0])


# Syntactical Candy #


def s(message, arg):
    """Syntactical candy:  sends a message."""
    return val.client.send_message(message.channel, arg)


# Code #


# Run the script.
val.client.run(val.app_token)
