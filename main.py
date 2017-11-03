# Version 1.1.5
#
#  ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #


# TODO: Figure out how to use inline to make more usable interfaces.
# TODO: Record user aliases { member.name, member.nick, member.mention }
# TODO: Log every command in a way that is reasonable.
# TODO: Properly document all parameters.


# Import #


import re

from discord import http, enums
from model import st, reg, val
from controller import util


# Events #


@val.client.event
async def on_ready():
    print('Logged in as')
    print(val.client.user.name)
    print(val.client.user.id)
    print('------')
    # TODO: Load in player prefs each time the bot starts.


@val.client.event
async def on_message(m):
    # List of commands.
    # TODO: !update to update an entry.
    fc = "forecast"
    nr = "newcharacter"
    lr = "listcharacters"
    sl = "skillroll"
    rt = "registercombat"
    nn = "newcanon"
    hp = "help"
    db = "debug"
    commands = [fc, nr, lr, sl, rt, hp, db]

    # # # # # # forecast command # # # # # #

    if m.content.startswith(val.command_prefix + " " + fc):
        # Format: [dice_pool, forecast_successes]

        args = m.content.split(',')

        # Check to make sure they didn't try to screw things up.
        if len(args) > 3:
            return await s(m, st.ERR_EXTRA_ARGS + '2')

        # Filter out non-numeric data
        for i in range(0, 2):
            args[i] = re.sub(reg.non_numeric, '', args[i])

        return await s(m, st.INF_BROKEN + " " + st.rand_slack())

    # # # # # # newcharacter command # # # # # #

    if m.content.startswith(val.command_prefix + " " + nr):
        # Ask the questions and add the character.
        e_nr = await util.add_character(m)
        if e_nr == val.escape_value:
            return s(m, st.ESCAPE)

        return await s(m, st.SAVED)

    # # # # # # listcharacters command # # # # # #

    if m.content.startswith(val.command_prefix + " " + lr):

        # Load in file.
        characters = util.get_characters()

        # Concatenate all names.
        all_names = "Character Names: \n"

        for name in characters:
            all_names += '► ' + name + '\n'

        return await s(m, all_names)

    # # # # # # skillroll command # # # # # #

    if m.content.startswith(val.command_prefix + " " + sl):
        # Format: <Type Command>

        # Begin the skill roll.
        final_string = await util.perform_skill_roll(m)
        if final_string == val.escape_value:
            return s(m, st.ESCAPE)

        return await s(m, final_string)

    # # # # # # registercombat command # # # # # #

    if m.content.startswith(val.command_prefix + " " + rt):
        # Format: <Type Command>

        e_rt = await util.reg_combat(m)
        if e_rt == val.escape_value:
            return s(m, st.ESCAPE)

        return await s(m, st.INF_DONE + " " + st.rand_slack())

    # # # # # # newcanon command # # # # # #

    if m.content.startswith(val.command_prefix + " " + nn):
        # Format: <Type Command>

        status = await util.make_canon(m, m.author)
        if status == val.escape_value:
            return s(m, st.ESCAPE)

        return await s(m, status + " " + st.rand_slack())

    # # # # # # help command # # # # # #

    if m.content.startswith(val.command_prefix + " " + hp):

        # TODO: Make strings into constants and make the help messages into a map.
        # TODO: Make all commands 'allcaps' to enforce the idea.
        # TODO: Make help send the commands to the user in a private message.

        help_message = "Commands are currently as follows: \n\n"

        if fc in m.content:
            help_message = st.FC_HELP
        elif nr in m.content:
            help_message = st.NR_HELP
        elif lr in m.content:
            help_message = st.LR_HELP
        elif sl in m.content:
            help_message = st.SL_HELP
        elif rt in m.content:
            help_message = st.SL_HELP
        elif db in m.content:
            help_message = st.DB_HELP
        else:
            for command in commands:
                help_message += command + '\n'
            help_message += "For more information use !help followed by a command to get more information. " \
                            "i.e. !help help."

        return await s(m, help_message)

    # # # # # # debug command # # # # # #

    if m.content.startswith(val.command_prefix + " " + db):
        # Format: <relative>

        # Learned:
        # You can reference members from mentions in messages by using member.mention.
        # Users are a valid destination for send_message()
        # Await will wait on that thread until the end of time; no branching messages
        # The bot can only proceed linearly for each callback performed.
        # Multithreading can circumvent the linear nature of the bot's callbacks.
        # With some serious finagling, you can link and create a channel and a category.

        return await s(m, st.INF_NAUGHT + " " + st.rand_slack())

    # # # # # # ...character # # # # # #

    if m.content == val.command_prefix or m.content == val.command_prefix + " ":
        # Format: <Fuck up command>
        return await s(m, st.UH + " " + st.rand_slack())


# Syntactical Candy #


def s(message, arg):
    """Syntactical candy:  sends a message."""
    return val.client.send_message(message.channel, arg)


# Code #


# Run the script.
val.client.run(val.app_token)
