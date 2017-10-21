# Version 1.1.4
#
#  ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #


# TODO: Figure out how to use inline to make more usable interfaces.


# Import #

import calc
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

    if message.content.startswith(val.command_prefix + fc):
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

    if message.content.startswith(val.command_prefix + nr):

        # Ask the questions and add the actor.
        e_nr = await util.add_actor(message)
        if e_nr == val.escape_value:
            return s(message, st.ESCAPE)

        return await s(message, st.SAVED)

    # # # # # # !listactors command # # # # # #

    if message.content.startswith(val.command_prefix + lr):

        # Load in file.
        actors = util.get_actors()

        # Concatenate all names.
        all_names = "Character Names: \n"

        for name in actors:
            all_names += '► ' + name + '\n'

        return await s(message, all_names)

    # # # # # # !skillroll command # # # # # #

    if message.content.startswith(val.command_prefix + sl):
        # Format: <Type Command>

        # Begin the skill roll.
        final_string = await util.perform_skill_roll(message)
        if final_string == val.escape_value:
            return s(message, st.ESCAPE)

        return await s(message, final_string)

    # # # # # # !help command # # # # # #

    if message.content.startswith(val.command_prefix + hp):

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

    if message.content.startswith(val.command_prefix + db):
        # Format: <relative>

        # TODO: Test edit_message
        # TODO: Test on_reaction
        # TODO: Test create_channel
        # TODO: Test mod bot ability to delete messages
        # TODO: Test making bot a mod of a specific channel

        test = await util.request_of_user(message, "TESTING REGEX", util.format_numer, expected_vars=1)
        return await s(message, test[0])


# Syntactical Candy #


def s(message, arg):
    """Syntactical candy:  sends a message."""
    return val.client.send_message(message.channel, arg)


# Code #


# Run the script.
val.client.run(val.app_token)
