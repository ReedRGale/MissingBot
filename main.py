# Version 1.2.0
#
#  ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #


# Import #


from model import st, val
from controller import util


# Init #


# I intend to overwrite this.
val.bot.remove_command("help")


# Events #


@val.bot.event
async def on_ready():
    print('Logged in as')
    print(val.bot.user.name)
    print(val.bot.user.id)
    print('------')

    # # # # # # # ...character # # # # # #
    #
    # if m.content == val.command_prefix or m.content == val.command_prefix + " ":
    #     # Format: <Fuck up command>
    #     return await s(m, st.UH + " " + st.rand_slack())

@val.bot.command(name="newcanon", help=st.NN_HELP, brief=st.NN_BRIEF)
async def new_canon(ctx):
    """Makes a new canon, including folders and player prefs."""
    status = await util.make_canon(ctx.message, ctx.message.author)
    if status == val.escape_value:
        return
    return await ctx.send(status + " " + st.rand_slack())


@val.bot.command(name="newcharacter", help=st.NR_HELP, brief=st.NR_BRIEF)
async def new_character(ctx):
    e_nr = await util.add_character(ctx.message, ctx.message.author, ctx.message.channel)
    if e_nr == val.escape_value:
        return
    return await ctx.send(st.SAVED)


@val.bot.command(name="listcharacters", help=st.LR_HELP, brief=st.LR_BRIEF)
async def list_characters(ctx):
    return await ctx.send(util.get_characters(ctx.message))


@val.bot.command(name="skillroll", help=st.SL_HELP, brief=st.SL_BRIEF)
async def skill_roll(ctx):
    # Begin the skill roll.
    final_string = await util.perform_skill_roll(ctx.message)
    if final_string == val.escape_value:
        return
    return await ctx.send(final_string)


@val.bot.command(name="newcombat", help=st.NT_HELP, brief=st.NT_BRIEF)
async def new_combat(ctx):
    e_rt = await util.new_combat(ctx.message)
    if e_rt == val.escape_value:
        return ctx.send(st.ESCAPE)

    return await ctx.send(st.INF_DONE + " " + st.rand_slack())


@val.bot.command(name="forecast", help=st.FT_HELP, brief=st.FT_BRIEF)
async def forecast(ctx, forecast, pool):
    """A command to accurately estimate a forecasted amount of success in a dice pool."""
    return await ctx.send(st.INF_BROKEN + " " + st.rand_slack())


@val.bot.command(name="help", help=st.HP_HELP, brief=st.HP_BRIEF)
async def help_command(ctx, *args):
    """Command to simplify referencing the help documents."""
    if args and len(args) == 1:  # If they want help with a specific command...
        await ctx.send(val.bot.get_command(args[0]).help)
    elif args:
        await ctx.send(st.ERR_EXTRA_ARGS)
    else:  # Otherwise print out all command briefs.
        await ctx.send("All Available Commands: \n\n")
        available_commands = val.bot.all_commands
        for name in available_commands:
            await ctx.send(name + ":  " + available_commands[name].brief + "\n")


@val.bot.command(name="debug", help=st.DB_HELP, brief=st.DB_BRIEF)
async def debug(ctx):
    """Command to test things."""
    # Learned:
    # You can reference members from mentions in messages by using member.mention.
    # Users are a valid destination for send_message()
    # Await will wait on that thread until the end of time; no branching messages
    # The bot can only proceed linearly for each callback performed.
    # Multithreading can circumvent the linear nature of the bot's callbacks.
    # With some serious finagling, you can link and create a channel and a category.

    await ctx.send(st.INF_NAUGHT + " " + st.rand_slack())


# Syntactical Candy #


def s(m, arg):
    """Syntactical candy:  sends a message."""
    return m.channel.send(content=arg)


# Code #


# Run the script.
val.bot.run(util.get_app_token())
