# Version 1.2.0
#
#  ----------- Script by ReedRGale ----------- #
# Designed to handle rolls for the Missing RP #


# Import #

import random
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
    TidyMessage.set_t_imgs(TidyMode.STANDARD.value, val.A_URLS_STANDARD)
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


@val.bot.command(name="newcanon", help=st.NN_HELP, brief=st.NN_BRIEF)
async def new_canon(ctx):
    """Makes a new canon, including folders and player prefs."""
    overruled = util.check_perms(ctx)
    if not overruled:
        status = await util.make_canon(ctx.message)
        if status == util.get_escape(ctx):
            return
        return await ctx.send(status + " " + st.rand_slack())
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="deletecanon", help=st.DN_HELP, brief=st.DN_BRIEF)
async def delete_canon(ctx):
    """Deletes a canon, though preserves folders and player prefs."""
    overruled = util.check_perms(ctx)
    if not overruled:
        status = await util.delete_canon(ctx.message)
        if status == util.get_escape(ctx):
            return
        elif not status:
            return
        return await ctx.send(status + " " + st.rand_slack())
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="newcharacter", help=st.NR_HELP, brief=st.NR_BRIEF)
async def new_character(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        e_nr = await util.add_character(ctx.message, ctx.message.author, ctx.message.channel)
        if e_nr == util.get_escape(ctx):
            return
        return await ctx.send(st.SAVED + " " + st.rand_slack())
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="listcharacters", help=st.LR_HELP, brief=st.LR_BRIEF)
async def list_characters(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        return await ctx.send(util.get_characters(ctx.message))
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="setescape", help=st.LR_HELP, brief=st.LR_BRIEF)
async def set_escape(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        prev_escape = util.get_escape(ctx)
        escape = await util.escape_setter(ctx)
        if escape == prev_escape:
            return
        return await ctx.send(st.INF_ESCAPE_SET.format(escape) + " " + st.rand_slack())
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="skillroll", help=st.SL_HELP, brief=st.SL_BRIEF)
async def skill_roll(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        # Begin the skill roll.
        final_string = await util.perform_skill_roll(ctx.message)
        if final_string == util.get_escape(ctx):
            return
        return await ctx.send(final_string)
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="newcombat", help=st.NT_HELP, brief=st.NT_BRIEF)
async def new_combat(ctx):
    overruled = util.check_perms(ctx)
    if not overruled:
        e_rt = await util.new_combat(ctx.message)
        if e_rt == util.get_escape(ctx):
            return
        return await ctx.send(st.INF_DONE + " " + st.rand_slack())
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="forecast", help=st.FT_HELP, brief=st.FT_BRIEF)
async def forecast(ctx, forecast, pool):
    """A command to accurately estimate a forecasted amount of success in a dice pool."""
    overruled = util.check_perms(ctx)
    if not overruled:
        return await ctx.send(st.INF_BROKEN + " " + st.rand_slack())
    return await ctx.send(overruled + " " + st.rand_slack())


@val.bot.command(name="help", help=st.HP_HELP, brief=st.HP_BRIEF)
async def help_command(ctx, *args):
    """Command to simplify referencing the help documents."""
    overruled = util.check_perms(ctx)
    if not overruled:
        if args and len(args) == 1:  # If they want help with a specific command...
            await ctx.send(val.bot.get_command(args[0]).help)
        elif args:
            await ctx.send(st.ERR_EXTRA_ARGS)
        else:  # Otherwise print out all command briefs.
            await ctx.send("Available Commands: \n\n")
            available_commands = val.bot.all_commands
            for name in available_commands:
                if util.check_perms(ctx, command=name):
                    await ctx.send(name + ":  " + available_commands[name].brief + "\n")
    return await ctx.send(overruled + " " + st.rand_slack())


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
    tm = await TidyMessage.build(ctx, util.get_escape(ctx), "Testing backend changes, type something.", req=True)
    tm = await tm.rebuild("Look ma, just one arg now!! Anyway, testing chains so go ahead and say something again.",
                          req=True)
    return await tm.rebuild("Poof, it's gone! Alright, easy. Chains work. Gonna have a few more things to test later.")


# Code #


# Run the script.
val.bot.run(util.get_app_token())
