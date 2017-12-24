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


# Events #


@val.bot.event
async def on_member_join(mem):
    # When player joins, update the player_prefs and update them.
    util.make_general_player_prefs(mem.guild)

    guild_path = "model\\" + str(mem.guild.id) + "\\" + st.CANONS_FN

    # For each canon, update the player_prefs and roles.
    if os.path.exists(guild_path):

        c_names = os.listdir(guild_path)
        for c in c_names:
            pref_path = guild_path + "\\" \
                        + c + "\\" \
                        + st.PLAYER_PREFS_FN + "\\" \
                        + str(mem.id) + ".json"

            open(pref_path, "a").close()
            with open(pref_path, "w") as fout:
                pref = {"user_type": UserType.OBSERVER.value, "relevant_character": None}
                json.dump(pref, fout, indent=1)

            with open(guild_path + "\\" + c + "\\" + st.ROLES_FN, "r") as fin:
                role_id = json.load(fin)[str(UserType.OBSERVER)]
                for r in mem.guild.roles:
                    if role_id == r.id:
                        role = r
                await mem.add_roles(role)


@val.bot.event
async def on_command(ctx):
    # On startup, check the general player_prefs and update them.
    util.make_general_player_prefs(ctx.guild)

    guild_path = "model\\" + str(ctx.guild.id) + "\\" + st.CANONS_FN

    # Only do this if the path exists already.
    if os.path.exists(guild_path):
        c_names = os.listdir(guild_path)

        # For each canon, make sure of the player_prefs and roles.
        for mem in ctx.guild.members:
            for c in c_names:
                if c != st.ARCHIVES_FN:
                    pref_path = guild_path + "\\" \
                                + c + "\\" \
                                + st.PLAYER_PREFS_FN + "\\" \
                                + str(mem.id) + ".json"

                    if not os.path.exists(pref_path):
                        open(pref_path, "a").close()
                        with open(pref_path, "w") as fout:
                            pref = {"user_type": UserType.OBSERVER.value, "relevant_character": None}
                            json.dump(pref, fout, indent=1)

                        with open(guild_path + "\\" + c + "\\" + st.ROLES_FN, "r") as fin:
                            role_id = json.load(fin)[str(UserType.OBSERVER)]
                            for r in mem.guild.roles:
                                if role_id == r.id:
                                    role = r
                            await mem.add_roles(role)


@val.bot.event
async def on_ready():
    print('Logged in as')
    print(val.bot.user.name)
    print(val.bot.user.id)
    print('------')

    # Prepare the TidyMessage metadata.
    TidyMessage.set_t_imgs(TidyMode.STANDARD.value, val.T_URLS_STANDARD)
    TidyMessage.set_t_imgs(TidyMode.WARNING.value, val.T_URLS_WARNING)
    TidyMessage.set_a_imgs(TidyMode.STANDARD.value, val.A_URLS_STANDARD)
    TidyMessage.set_a_imgs(TidyMode.WARNING.value, val.A_URLS_WARNING)
    TidyMessage.set_color(TidyMode.STANDARD.value, 0xF2D40F)
    TidyMessage.set_color(TidyMode.WARNING.value, 0xc99e3a)
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
async def help_command(ctx, *args):
    """Command to simplify referencing the help documents."""
    overruled = util.check_perms(ctx)
    if not overruled:
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
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="setescape", help=st.SE_HELP, brief=st.SE_BRIEF)
async def set_escape(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        return await util.escape_setter(ctx)
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="newcanon", help=st.NN_HELP, brief=st.NN_BRIEF)
async def new_canon(ctx):
    """Makes a new canon, including folders and player prefs."""
    overruled = util.check_perms(ctx)
    if not overruled:
        return await util.make_canon(ctx)
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="deletecanon", help=st.DN_HELP, brief=st.DN_BRIEF)
async def delete_canon(ctx):
    """Deletes a canon, though preserves folders and player prefs."""
    overruled = util.check_perms(ctx)
    if not overruled:
        return await util.delete_canon(ctx)
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="newcharacter", help=st.NR_HELP, brief=st.NR_BRIEF)
async def new_character(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        return await util.add_character(ctx)
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="listcharacters", help=st.LR_HELP, brief=st.LR_BRIEF)
async def list_characters(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        return await util.get_characters(ctx)
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="skillroll", help=st.SL_HELP, brief=st.SL_BRIEF)
async def skill_roll(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        # Begin the skill roll.
        return await util.perform_skill_roll(ctx)
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="newcombat", help=st.NT_HELP, brief=st.NT_BRIEF)
async def new_combat(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        return await util.new_combat(ctx.message)
    return await TidyMessage.build(ctx, util.get_escape(ctx), req=False, content=overruled + " " + st.rand_slack(),
                                   mode=TidyMode.WARNING)


@val.bot.command(name="debug", help=st.DB_HELP, brief=st.DB_BRIEF)
async def debug(ctx, *args):
    """Command to test things."""
    # Learned:
    # You can reference members from mentions in messages by using member.mention.
    # Users are a valid destination for send_message()
    # Await will wait on that thread until the end of time; no branching messages
    # The bot can only proceed linearly for each callback performed.
    # Multithreading can circumvent the linear nature of the bot's callbacks.
    # With some serious finagling, you can link and create a channel and a category.
    # Worked out TidyMessage kinks.
    return await TidyMessage.build(ctx, util.get_escape(ctx), content="Nothing to see here!", req=False)

# Code #


# Run the script.
val.bot.run(util.get_app_token())
