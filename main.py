# Version 1.2.0
#
#  ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #


# Import #

import discord
import os
import json
import shlex

from pprint import pprint
from discord.ext.commands import Group, Command
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

    async def call(*args):
        # Retrieve context and args.
        ctx = args[0]
        args = tuple(shlex.split(ctx.message.content)[2:])

        # Update the guild state.
        await update_guild(ctx)

        # Check if the command is overruled.
        overruled = util.check_perms(ctx)

        # Check if a command has already been called by this user.
        if not overruled and not val.calling.get(ctx.message.author.id):
            await command(ctx, args)
        elif overruled:
            await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                    content=overruled + " " + st.rand_slack(),
                                    mode=TidyMode.WARNING)

        # Unlock command functionality.
        val.calling[ctx.message.author.id] = False
    return call


# Events #


@val.bot.event
async def on_member_join(mem):
    # When player joins, update the player_prefs and update them.
    util.update_g_player_prefs(mem.guild)

    # Path syntactical candy.
    g = str(mem.guild.id)
    m = str(mem.id)

    # For each canon, update the player_prefs and roles.
    if os.path.exists(st.CANONS_P.format(g)):
        canon_names = os.listdir(st.CANONS_P.format(g))
        for canon in canon_names:
            # Set up the individual's player prefs.
            open(st.C_PLAYER_PREF_P.format(g, canon, m), 'a').close()
            with open(st.C_PLAYER_PREF_P.format(g, canon, m), 'w') as fout:
                pref = {st.FLD_UTYPE: UserType.OBSERVER.value, st.FLD_RCHAR: None}
                json.dump(pref, fout, indent=1)

            # Set up the player's roles.
            with open(st.ROLES_P.format(g, canon), 'r') as fin:
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
    print("Logged in as")
    print(val.bot.user.name)
    print(val.bot.user.id)
    print("Systems are a-go boss!")

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
    val.perms[st.FULL_HELP] = ()
    val.perms[st.FULL_DEBUG] = ()
    val.perms[st.FULL_NEW_CAN] = ()
    val.perms[st.FULL_NEW_COM] = (UserType.GM.value, UserType.PLAYER.value)
    val.perms[st.FULL_DEL_CAN] = (UserType.GM.value,)
    val.perms[st.FULL_EDT_ESC] = ()


# GROUPLESS COMMANDS #


@val.bot.command(name=st.COMM_HELP, help=st.HELP_HELP, brief=st.HELP_BRIEF)
@call_command
async def help_command(ctx, args):
    """Command to simplify referencing the help documents."""
    available_commands = val.bot.all_commands
    if args:  # If they want help with a specific command or group...
        arg = 0  # The argument we're evaluating at the moment.
        command = available_commands.get(args[arg])  # The current level of command we're on.
        done = lambda x: x >= len(args)

        # Iterate over all args and determine correct help string to give.
        while not done(arg):
            arg += 1  # Lookahead by one argument.
            if isinstance(command, Group) and not done(arg):
                command = command.get_command(args[arg])
            elif isinstance(command, Group) and done(arg):
                help_string = st.INF_COMMAND_GROUP
                for child in command.commands:
                    if isinstance(child, Group):
                        help_string += st.itlc(st.INF_GROUP) + " " \
                                       + st.bold(child.name) + ":  " + child.brief + "\n\n"
                    else:
                        help_string += st.itlc(st.INF_COMMAND) + " " \
                                       + st.bold(child.name) + ":  " + child.brief + "\n\n"
                await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, content=help_string,
                                        req=False, mode=TidyMode.STANDARD)
            elif isinstance(command, Command) and not done(arg):
                return await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                               content=st.ERR_NO_SUCH_CHILD.format(args[arg - 1], args[arg]),
                                               mode=TidyMode.WARNING)
            elif isinstance(command, Command) and done(arg):
                await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                        content=st.INF_HELP.format(command.name, command.help),
                                        mode=TidyMode.STANDARD)
            elif not done(arg):
                return await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                               content=st.ERR_NO_SUCH_TYPE.format(args[arg - 1], args[arg]),
                                               mode=TidyMode.WARNING)
            elif done(arg):
                if arg == 1 and st.KEYWORDS.get(args[arg - 1]):  # Keyword checks should only ever be one arg.
                    await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                            content=st.INF_HELP.format(args[arg - 1],
                                                                       st.KEYWORDS.get(args[arg - 1]),
                                            mode=TidyMode.STANDARD))
                else:
                    return await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                                   content=st.ERR_NO_SUCH_CHILD.format(args[arg - 2], args[arg - 1]),
                                                   mode=TidyMode.WARNING)
    else:  # Otherwise print out all command briefs.
        # Prepare the string.
        help_string = st.INF_TOP_LEVEL_COMMANDS
        for name in available_commands:
            if isinstance(available_commands[name], Group):
                help_string += st.itlc(st.INF_GROUP) + "  " \
                               + st.bold(name) + ":  " + available_commands[name].brief + "\n\n"
            else:
                help_string += st.itlc(st.INF_COMMAND) + "  " \
                               + st.bold(name) + ":  " + available_commands[name].brief + "\n\n"
        await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, content=help_string,
                                req=False, mode=TidyMode.STANDARD)


#  NEW COMMANDS  #


@val.bot.group(name=st.COMM_NEW, help=st.NEW_HELP, brief=st.NEW_BRIEF)
async def new(ctx):
    """Group of commands designated to create things."""
    if ctx.invoked_subcommand is None:
        await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                content=st.ERR_NEW_WHAT, mode=TidyMode.WARNING)


@new.command(name=st.COMM_CANON, help=st.NN_HELP, brief=st.NN_BRIEF)
@call_command
async def new_canon(ctx, args):
    """Makes a new canon, including folders and player prefs."""
    return await util.new_canon(ctx)


@new.command(name=st.COMM_COMBAT, help=st.NT_HELP, brief=st.NT_BRIEF)
@call_command
async def new_combat(ctx, args):
    return await util.new_combat(ctx.message)


#  DELETE COMMANDS  #


@val.bot.group(name=st.COMM_DEL, help=st.DLTE_HELP, brief=st.DLTE_BRIEF)
async def delete(ctx):
    """Group of commands designated to remove things."""
    if ctx.invoked_subcommand is None:
        await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                content=st.ERR_DELETE_WHAT, mode=TidyMode.WARNING)


@delete.command(name=st.COMM_CANON, help=st.DN_HELP, brief=st.DN_BRIEF)
@call_command
async def delete_canon(ctx, args):
    """Deletes a canon, though preserves folders and player prefs."""
    return await util.delete_canon(ctx)


#  EDIT COMMANDS  #


@val.bot.group(name=st.COMM_EDT, help=st.EDIT_HELP, brief=st.EDIT_BRIEF)
async def edit(ctx):
    """Group of commands designated to edit data."""
    if ctx.invoked_subcommand is None:
        await TidyMessage.build(ctx, util.get_escape(ctx), st.ESCAPE, req=False,
                                content=st.ERR_EDIT_WHAT, mode=TidyMode.WARNING)


@edit.command(name=st.COMM_ESC, help=st.SE_HELP, brief=st.SE_BRIEF)
@call_command
async def edit_escape(ctx, args):
    return await util.escape_setter(ctx)


# DEBUG COMMANDS  #


@val.bot.group(name=st.COMM_DEBUG, help=st.DB_HELP, brief=st.DB_BRIEF)
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
    available_commands = val.bot.all_commands
    for name in available_commands:
        print(name)


#  Helper Functions  #


async def update_guild(ctx):
    # On startup, check the general player_prefs and update them.
    util.update_g_player_prefs(ctx.guild)

    # Path syntactical candy.
    g = str(ctx.guild.id)

    # For each canon, if it exists, make sure of the player_prefs and roles.
    if os.path.exists(st.CANONS_P.format(g)):
        canon_names = os.listdir(st.CANONS_P.format(g))
        for mem in ctx.guild.members:
            for c in canon_names:
                if c != st.ARCHIVES_FN:  # Ignore _archives folder...
                    if not st.C_PLAYER_PREF_P.format(g, c, mem.id):  # If player_pref not found...
                        open(st.C_PLAYER_PREF_P.format(g, c, mem.id), 'a').close()
                        with open(st.C_PLAYER_PREF_P.format(g, c, mem.id), 'w') as fout:
                            pref = {st.FLD_UTYPE: UserType.OBSERVER.value, st.FLD_RCHAR: None}
                            json.dump(pref, fout, indent=1)
                        with open(st.ROLES_P.format(g, c), 'r') as fin:
                            role_id = json.load(fin)[str(UserType.OBSERVER)]
                            for r in mem.guild.roles:
                                if role_id == r.id:
                                    role = r
                            await mem.add_roles(role)
                    for role in mem.roles:
                        with open(st.ROLES_P.format(g, c), 'r') as fin:
                            c_roles = json.load(fin)
                            if role.id in c_roles.values():  # If role is canon role...
                                # If role isn't the role in their prefs...
                                u_type = util.get_user_type(mem, val.bot.get_channel(int(c)).channels[0])
                                if c_roles[UserType(u_type).name] != role.id:
                                    await role.delete(reason=st.ERR_DUP_ROLES)


# Code #


# Run the script.
val.bot.run(util.get_app_token())
