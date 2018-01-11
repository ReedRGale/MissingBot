# Version 1.2.0
#
#  ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #


# Import #

import discord
import os
import json

from model import st, val
from model.enums import UserType, TidyMode
from view.TidyMessage import TidyMessage
from controller import util


# Init #


# I intend to overwrite this.
val.bot.remove_command("help")


# Wrappers #


def call_command(command):
    """Decorator that takes a command, updates the bot's guild state and wraps it in checks.
    If it fails any of the checks, it'll route it to the proper exit."""

    async def checks(*args):
        # Retrieve context.
        ctx = args[0]

        # Check if the command is overruled.
        await update_guild(ctx)
        overruled = util.check_perms(ctx)

        # Check if a command has already been called by this user.
        if not overruled and not val.calling.get(ctx.message.author.id):
            await command(*args)
        elif overruled:
            await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                    content=overruled + " " + st.rand_slack(),
                                    mode=TidyMode.WARNING)

        # Unlock command functionality.
        val.calling[ctx.message.author.id] = False
    return checks


# Events #


@val.bot.event
async def on_member_join(mem):
    # When player joins, update the player_prefs and update them.
    util.make_general_player_prefs(mem.guild)

    # Path syntactical candy.
    g = str(mem.guild.id)
    m = str(mem.id)

    # For each canon, update the player_prefs and roles.
    if os.path.exists(st.CANONS_P.format(g)):
        canon_names = os.listdir(st.CANONS_P.format(g))
        for canon in canon_names:
            # Set up the individual's player prefs.
            open(st.C_PLAYER_PREF_P.format(g, canon, m), "a").close()
            with open(st.C_PLAYER_PREF_P.format(g, canon, m), "w") as fout:
                pref = {"user_type": UserType.OBSERVER.value, "relevant_character": None}
                json.dump(pref, fout, indent=1)

            # Set up the player's roles.
            with open(st.ROLES_P.format(g, canon), "r") as fin:
                role_id = json.load(fin)[str(UserType.OBSERVER)]
                for r in mem.guild.roles:
                    if role_id == r.id:
                        role = r
                await mem.add_roles(role)


@val.bot.event
async def on_command(ctx):
    # Record anyone calling a command.
    if ctx.message.author.id not in val.calling:
        val.calling[ctx.message.author.id] = True


@val.bot.event
async def on_ready():
    print('Logged in as')
    print(val.bot.user.name)
    print(val.bot.user.id)
    print('------')

    # Prepare the TidyMessage metadata.
    TidyMessage.set_t_imgs(TidyMode.STANDARD.value, val.T_URLS_STANDARD)
    TidyMessage.set_t_imgs(TidyMode.WARNING.value, val.T_URLS_WARNING)
    TidyMessage.set_t_imgs(TidyMode.PROMPT.value, val.p_avatar)

    TidyMessage.set_a_imgs(TidyMode.STANDARD.value, val.A_URLS_STANDARD)
    TidyMessage.set_a_imgs(TidyMode.WARNING.value, val.A_URLS_WARNING)
    TidyMessage.set_a_imgs(TidyMode.PROMPT.value, val.p_avatar)

    TidyMessage.set_color(TidyMode.STANDARD.value, 0xF2D40F)
    TidyMessage.set_color(TidyMode.WARNING.value, 0xc99e3a)
    TidyMessage.set_color(TidyMode.PROMPT.value, val.p_color)

    TidyMessage.set_url(val.GITHUB_URL)

    # Load in Permissions for Users
    val.perms["newcanon"] = ()
    val.perms["deletecanon"] = (UserType.GM.value,)
    val.perms["newcharacter"] = (UserType.GM.value,)
    val.perms["listcharacters"] = (UserType.GM.value, UserType.PLAYER.value, UserType.OBSERVER.value)
    val.perms["skillroll"] = (UserType.GM.value, UserType.PLAYER.value, UserType.OBSERVER.value)
    val.perms["newcombat"] = (UserType.GM.value, UserType.PLAYER.value)
    val.perms["forecast"] = (UserType.GM.value, UserType.PLAYER.value, UserType.OBSERVER.value)
    val.perms["help"] = ()
    val.perms["setescape"] = ()
    val.perms["debug"] = ()


# Commands #


@val.bot.command(name="help", help=st.HP_HELP, brief=st.HP_BRIEF)
@call_command
async def help_command(ctx, *args):
    """Command to simplify referencing the help documents."""
    if args and len(args) == 1:  # If they want help with a specific command...
        try:
            await TidyMessage.build(ctx, util.get_escape(ctx), content=val.bot.get_command(args[0]).help,
                                    req=False, mode=TidyMode.STANDARD)
        except discord.ext.commands.errors.CommandInvokeError:
            await TidyMessage.build(ctx, util.get_escape(ctx), content=st.ERR_WHAT,
                                    req=False, mode=TidyMode.WARNING)
    elif args:
        await TidyMessage.build(ctx, util.get_escape(ctx), content=st.ERR_EXTRA_ARGS.format("one"),
                                req=False, mode=TidyMode.STANDARD)
    else:  # Otherwise print out all command briefs.
        # Prepare the string.
        help_string = "Available Commands: \n\n"
        available_commands = val.bot.all_commands
        for name in available_commands:
            help_string += "**" + name + "**" + ":  " + available_commands[name].brief + "\n\n"
        return await TidyMessage.build(ctx, util.get_escape(ctx), content=help_string,
                                       req=False, mode=TidyMode.STANDARD)


@val.bot.command(name="setescape", help=st.SE_HELP, brief=st.SE_BRIEF)
@call_command
async def set_escape(ctx):
    return await util.escape_setter(ctx)


@val.bot.command(name="newcanon", help=st.NN_HELP, brief=st.NN_BRIEF)
@call_command
async def new_canon(ctx):
    """Makes a new canon, including folders and player prefs."""
    return await util.make_canon(ctx)


@val.bot.command(name="deletecanon", help=st.DN_HELP, brief=st.DN_BRIEF)
@call_command
async def delete_canon(ctx):
    """Deletes a canon, though preserves folders and player prefs."""
    return await util.delete_canon(ctx)


@val.bot.command(name="newcharacter", help=st.NR_HELP, brief=st.NR_BRIEF)
@call_command
async def new_character(ctx):
    return await util.add_character(ctx)


@val.bot.command(name="listcharacters", help=st.LR_HELP, brief=st.LR_BRIEF)
@call_command
async def list_characters(ctx):
    return await util.get_characters(ctx)


@val.bot.command(name="skillroll", help=st.SL_HELP, brief=st.SL_BRIEF)
@call_command
async def skill_roll(ctx):
    return await util.perform_skill_roll(ctx)


@val.bot.command(name="newcombat", help=st.NT_HELP, brief=st.NT_BRIEF)
@call_command
async def new_combat(ctx):
    return await util.new_combat(ctx.message)


@val.bot.command(name="debug", help=st.DB_HELP, brief=st.DB_BRIEF)
@call_command
async def debug(ctx):
    """Command to test things."""
    # Learned:
    # You can reference members from mentions in messages by using member.mention.
    # Users are a valid destination for send_message()
    # Await will wait on that thread until the end of time; no branching messages
    # The bot can only proceed linearly for each callback performed.
    # Multithreading can circumvent the linear nature of the bot's callbacks.
    # With some serious finagling, you can link and create a channel and a category.
    # Worked out TidyMessage kinks.
    # When ensure_future is called, all coros are called!
    print("You're in.")


# Helper functions

async def update_guild(ctx):
    # On startup, check the general player_prefs and update them.
    util.make_general_player_prefs(ctx.guild)

    # Path syntactical candy.
    g = str(ctx.guild.id)

    # Only do this if the path exists already.
    if os.path.exists(st.CANONS_P.format(g)):
        canon_names = os.listdir(st.CANONS_P.format(g))

        # For each canon, make sure of the player_prefs and roles.
        for mem in ctx.guild.members:
            for canon in canon_names:
                if canon != st.ARCHIVES_FN:
                    if not st.C_PLAYER_PREF_P.format(g, canon, mem.id):
                        # Set up the individual's player prefs.
                        open(st.C_PLAYER_PREF_P.format(g, canon, mem.id), "a").close()
                        with open(st.C_PLAYER_PREF_P.format(g, canon, mem.id), "w") as fout:
                            pref = {"user_type": UserType.OBSERVER.value, "relevant_character": None}
                            json.dump(pref, fout, indent=1)

                        # Set up the player's roles.
                        with open(st.ROLES_P.format(g, canon), "r") as fin:
                            role_id = json.load(fin)[str(UserType.OBSERVER)]
                            for r in mem.guild.roles:
                                if role_id == r.id:
                                    role = r
                            await mem.add_roles(role)

# Code #


# Run the script.
val.bot.run(util.get_app_token())
