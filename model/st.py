# ----------- Script by ReedRGale ----------- #
# String constants used in the scripts. #


# Imports #


import random


# Command Names #


COMM_HELP = "help"
COMM_DEBUG = "debug"
COMM_NEW = "new"
COMM_CANON = "canon"
COMM_DEL = "delete"
COMM_EDT = "edit"
COMM_ESC = "escape"
COMM_COMBAT = "combat"
COMM_PREFIX = "~dd "
COMM_UNF = "unaffiliated"

FULL_HELP = "_" + COMM_HELP
FULL_DEBUG = "_" + COMM_DEBUG
FULL_NEW_CAN = "_".join([COMM_NEW, COMM_CANON])
FULL_NEW_COM = "_".join([COMM_NEW, COMM_COMBAT])
FULL_DEL_CAN = "_".join([COMM_DEL, COMM_CANON])
FULL_EDT_ESC = "_".join([COMM_EDT, COMM_ESC])


# Informative Messages #


INF_DONE = "The thing you asked for should be done now."
INF_NAUGHT = "Nothing to see here."
INF_BROKEN = "I know. It's broken. I'll get to it when I get to it."
INF_CHANNELS_MADE = "Alright bud, I think things are set in place. Your private combat channel is made " \
                    "and should be called: "
INF_CANON_MADE = "All the paperwork is in order. Enjoy the new world, I guess."
INF_CANON_SET = "Well, here you are. Enjoy your stay or something."
INF_NOT_GM = "Wise choice. I'll let that jerk know you don't want any part of this nonsense."
INF_DENIED_GM = "They made the smart choice and chose not to be GM. Call me again when you have someone for the job." \
                "Hint:  maybe try asking them first??"
INF_DENIED_DELETE = "Seems people still like this world. At the very least, the vote failed. The show goes on, for now."
INF_DELETE_CHANNEL = "I zorked this because I was told to by the GM and the players voted for it."
INF_DELETE_ROLE = "I blanged this because I was told to by the GM and the players agreed."
INF_ESCAPE_SET = "Your new escape value is {}. Use it wisely."
INF_MESSAGING_D = "I'll get the word out, then. I guess it's time to see if this canon gets to live."
INF_REVIVE_ABORT = "Yeah, yeah, true. There's a reason it was let go, after all. Let sleeping dogs lie. Call me " \
                   "again if you have a new name for your canon."
INF_REVIVE_A_GO = "Cool cool. Let's get this reboot started!\n\n"
INF_COMMAND_GROUP = "Here's everything I know about this group of commands: \n\n"
INF_HELP = "Here's what I know about '{}:' \n\n{}"
INF_TOP_LEVEL_COMMANDS = "Here's all the major command types. If you want to delve them further, " \
                         "I've left more on calling specific types, call '~dd help help'. Thank.\n\n"
INF_GROUP = "<Command-Group>"
INF_COMMAND = "<Command>"
INF_HEY_THERE = "Hiya! You called?" \
                "\n\nHmm... figure I should give some useful information. I'm DJ Dante, " \
                "here to help you remix canons by facilitating your roleplays! I have a lot of features " \
                "(if Mr. Programmer is done creating this portal for me to talk to you, anyway) and " \
                "if you want to know more about them, I'd recommend calling '" + COMM_PREFIX + COMM_HELP + "'!"

SAVED = "Databank updated, for whatever reason it needed updating!"
ESCAPE = "I'll escape the command, but just because you asked nicely. ;>"


# Request Messages #


REQ_STATS = "Which stats are related to this roll? Separate with spaces. \n"
REQ_ACTIVE_CHARACTER = "Which character is rolling? \n"
REQ_CHARACTER = "So what's this character's {} value?"
REQ_MOD_REASON = "What's one factor affecting this roll?"
REQ_ROLL_PURPOSE = "What's this skill roll for?"
REQ_MOD_AMOUNT = "By how many dice should this affect the roll? (i.e. -3, 4, 1, 2, etc...)"
REQ_CANON = "Alright... so what canon are we working with today?"
REQ_NEW_CANON = "So, what'cha wanna call this new story-world?"
REQ_USER_COMBAT = "Now, which users are taking part in this 'glorious brawl?' You know the drill, " \
                  "list them all with at tags (@) and separate them with spaces. Ah, do note that the GM " \
                  "is automatically included. No need to worry there. \n\n " \
                  "Ex: @DJ Dante , @ReedRGale"
REQ_PLAYER = "So, which player is gonna to be using this character? Remember to use their taggable name. You know, " \
             "the one with the '@' in it?"
REQ_USER_GM = "Okay. So who's gonna be running this show? If it's you, tag yourself. Otherwise, tag someone else."
REQ_REL_CANON = "Alright, so what canon is your poison today?"
REQ_NEW_ESCAPE = "So, tell me what your new escape value is gonna be. Just try not to make it something you might " \
                 "say normally like your character's name, because whenever I see it, I'm gonna blindly end the " \
                 "command, 'kay?"


# Confirmations #


ASK_IF_MODS = "Are there modifications to this roll? You know, those things that might change the roll value?"
ASK_IF_MORE_MODS = "Any more modifications to make?"
ASK_IF_FIGHT = "So, someone challenged you to combat. You gonna make that fight happen in canon?"
ASK_IF_GM = "Are you really sure you want to do this? Managing an RP is hard and you might have just been " \
            "nominated for something you don't want to do. If so, just tell me 'no.' If not... well, your funeral. " \
            "You know what they say about funerals though. Can't spell it without 'fun.' \n\n" \
            "Anyway. What'll it be? Will you be this canon's god (world/RP)?"
ASK_IF_DELETE = "So, seems the time for this world has come to a close... according to a GM anyway. Do you agree? " \
                "Yes? No? Nothing in between now, I don't like ambiguity when it comes to these things."
ASK_REVIVE_RP = "Ah. So my files indicate this RP existed before. So, uh, I'm not gonna overwrite it with your " \
                "new one. Buuuut... we could bring this back. What'd'ya say?"


# Error Messages #


ERR_REPEAT_1 = "Let's try that again."
ERR_REPEAT_2 = "Try again. With feeling this time."

ERR_EXTRA_ARGS = "Whoa there pardner. That's a lot of arguments. Try to keep it to around {}, okay?"
ERR_WHAT = "Uh... what now?"
ERR_NOT_ENOUGH_ARGS = "Hey. Buddy. You need at least this many arguments to use this command: "
ERR_PLAYER_EXIST = "Yo. So... uh... don't try to like... take this character's identity. K? They already exist. " \
                   "Let 'em be."
ERR_NOT_INT = "Hey so, this is looking for numerical integer data. In layman's term's, that's numbers without the " \
              "'.' in them. i.e 1, 2, 3 and not 3.4, 1.23, etc. So anyway. Try again."
ERR_MEMBER_NONEXIST = "Hey, so... seems that the member '{}' isn't in this server. Maybe try again, yeah?"
ERR_PLAYER_NONEXIST = "Yo. So... uh... I don't know how to put this nicely. But... that player doesn't... exist? Yeah."
ERR_CANON_NONEXIST = "Okay so... these worlds aren't real, but this one exists less than the other " \
                     "worlds that don't exist. That is, I don't have it in my records."
ERR_ONLY_ONE_GM = "Alright, let's start with just one GM. Simplifies things for now. Later you can add multiple GMs. " \
                  "But for now... let's keep it simple."
ERR_NOT_IN_CANON = "This channel isn't in a canon. Try calling this command somewhere it would, y'know, _work_."
ERR_INV_ARG = "Sorry, don't know that keyword "
ERR_DUP_ARG = "So it looks like you've used the same arg multiple times for some reason. Could you, like, not?"
ERR_INV_FORM = "Invalid. Once more, with feeling this time."
ERR_STAT_LT_ZERO = "A stat can't be less than 0. And, let's be fair, do you really want it to be?"
ERR_STAT_GT_FIFT = "A stat can't be greater than 15. And that's already obnoxiously high as it is."
ERR_NOT_YES_OR_NO = "Sorry, that doesn't look affirmative or negatory, boss. If worst comes to worst, " \
                    "don't be creative. A simple 'yes' or 'no' would suffice. So once more. With feeling this time."
ERR_CANON_EXISTS = "This world is kind of already a thing. Don't like, get all up in its biz' ya dig?"
ERR_NOT_IN_RP = "Hey. This person is just an observer here. What're ya tryin to pull?"
ERR_NOT_IN_GUILD = "Okay so maybe you really like that person. But they aren't here. I can't work with people that " \
                   "aren't here."
ERR_VOTE_FAILED = "So... something went wrong with the vote. Like, pretty darn wrong. Like, we have more members " \
                  "voting than are in the canon kind of wrong. Let's uh... let's call the command a later time and " \
                  "see if we can't do something about that."
ERR_INSUF_PERMS = "Nice try, but you don't have the permissions to call this."
ERR_IN_CANON = "This command is only intended to be called outside a canon. In general, this is to avoid clutter " \
               "in the RP itself. You dig me?"
ERR_INV_USER_CONTENT_I = "Hey so, it looks like your input is, like, invalid in some way. Specifically, you're " \
                         "using one of these:  {}. If you could stop doing that, it would make your " \
                         "command a lot easier to process, kthx."
ERR_INV_USER_CONTENT_V = "Alright so, gonna let you in on a little secret. I'm looking for specific words. " \
                         "This might get lengthy, but I'm looking for... \n\n{}. \n\nCould ya use one of those? " \
                         "Pretty please?"
ERR_INVALID_TM_CONTENT = "Mr. Programmer, somehow you've failed to give me a string or an Embed to show our lovely " \
                         "users. Tut tut. Get on that."
ERR_INVALID_TIDYMODE = "Mr. Programmer, it looks like you gave me a TidyMode I don't know how to work with. " \
                       "And now, some user is probably going 'huh? what's that?' You only have yourself to blame " \
                       "now, Mr. Programmer. After all, you wrote this error code."
ERR_TOO_FEW_ARGS = "Soooo, I'm looking for a few more arguments than that. Specifically, I'm looking for {} {}."
ERR_TOO_MANY_ARGS = "Bit overkill there. I'm looking for a little less than that. Specifically, {} {}. If you want to" \
                    " have two words in one word here, surround it with quotation marks like \"this is!\""
ERR_INEXACT_ARGS = "Noooot exactly. I'm looking for '{}' arg here. If you want to" \
                    " have two words in one word here, surround it with quotation marks like \"this is!\""
ERR_REPEAT_VAL = "So, you don't repeat variables here. Please. You know the one I'm talking about. " \
                 "'{}.' Don't do that."
ERR_NOT_IN_ALIAS = "I don't know the word '{}' in this context. Maybe try again?"
ERR_NO_SUCH_CHILD = "Uhh, the command '{}' doesn't have a child command called '{}.'"
ERR_NO_SUCH_TYPE = "So, I looked, and I don't have any command in my database called '{}.' Not under '{}' anyway. " \
                   "Sorry fam."
ERR_NO_SUCH_KEYWORD = "Sadly, I can't find a keyword in your canon called '{}.' Them's the breaks."
ERR_DELETE_WHAT = "...delete what now?"
ERR_HELP_WHAT = "...sorry I can't help with nonsense."
ERR_NEW_WHAT = "...sorry, I can't create every random thing you come up with."
ERR_DUP_ROLES = "You can't have multiple roles in a canon!!"
ERR_MEMBER_DANTE = "Flattering as you are, I am not a legal target for this. Cute sentiment though."
ERR_MEMBER_BOT = "'{}' is a bot. Don't try to use bots as the targets for commands, silly. They can't RP. " \
                 "Except for me. ...Not that I'm considered a legal target for the command either. ;u;\n\n"
ERR_INV_USER_CONTENT_NOT_ALNUM = "'{}' isn't alphanumeric. That is... you put weird stuff in it. This can " \
                                 "cause issues when making files or channels and junk. Take out the weird " \
                                 "characters this time."


# File Names #


MODEL_FN = "model"
ARCHIVES_FN = "_archives"
GENERAL_FN = "general"
GUILDS_FN = "guilds"
CHARACTERS_FN = "characters"
KEYWORDS_FN = "keywords"
META_FN = "meta"
LOGS_FN = "logs"
CANONS_FN = "canons"
COMMANDS_FN = "commands"
PLAYER_PREFS_FN = "player_prefs"
ROLES_FN = "roles.json"
EXCEPTIONS_FN = "command_exceptions.json"
IDS_FN = "canon_ids.json"


# Canon Channels #


CHNL_INTRO = "_intro"
CHNL_IC = "_IC"
CHNL_OOC = "_OOC"
CHNL_COMM = "_command_room"
CHNL_RULE = "_rules"
CHNL_META = "_meta"
CHNL_NOTE = "_gm_notes"
CHNL_READ = "_archive"
CHNL_ALL = [CHNL_INTRO, CHNL_IC, CHNL_OOC, CHNL_COMM, CHNL_RULE, CHNL_META, CHNL_NOTE, CHNL_READ]


# JSON Fields #


FLD_ESC = "escape"
FLD_PAGE = "page"
FLD_TTLE = "title"
FLD_CNTT = "content"
FLD_MODE = "mode"
FLD_PATH = "path"
FLD_EDTBL = "editable"
FLD_UTYPE = "user_type"
FLD_RCHAR = "relevant_character"
FLD_CHNL = "channels"
FLD_ROLE = "roles"


# Comparison Modes #

MODE_GT = ">"
MODE_GTE = ">="
MODE_LT = "<"
MODE_LTE = "<="
MODE_EQ = "=="


# Help Messages #


HELP_BRIEF = "This is the command you're calling right now. Woohoo."
HELP_HELP = "Alright, I assume you're here because it was in the main command. Here's the skinny, and I'll try to " \
            "keep it short and sweet. Commands are put in groups. Those groups of commands can have groups. " \
            "Ya follow me so far? Cool. \n\nSo when you call 'help' you should denote all the groups that own " \
            "that command. I know that might sound weird, so let me give you and example, 'kay? \n\n" \
            "If you wanted to know about the command '" + COMM_PREFIX + COMM_NEW + " " + COMM_CANON + \
            "' you would call '~dd help new canon' instead of '~dd help canon' because without knowing it's for a " \
            "'new' canon, I can't know for sure what you're talking about.\n\nBasically, just call it like you would " \
            "normally but instead preface it with '~dd help' instead of just '~dd'. \n\nPretty intuitive, " \
            "right? Also, if there are important keywords defined by your GM, I store them under the help command as " \
            "well. it's just '~dd <keyword>.' Simple enough, I think.\n\n" \
            "Now you know how to ask me for something specific, so you should be ready to use my features. " \
            "Play nice with me. ^_^"

NEW_BRIEF = "This is for commands that create something."
NEW_HELP = "A lot of commands are going to end up having me make stuff. That is, they'll have me _do work._ Snore. " \
           "But in general, with this kind of work, I'll be recording new information, making channels, roles, " \
           "permissions, character logs, rules... the works. \n\nDon't work me too hard, yeah? ;u;"

DLTE_BRIEF = "A group of commands where I break shit. Gracefully."
DLTE_HELP = "You call a delete command, and I'm going to be ~~tearing up records with gleeful abandon~~ carefully " \
            "and neatly ascertain the data that needs to be deleted based off your command. Usually there some sort " \
            "of failsafe to stop you from accidentally deleting something, but I wouldn't rely on that necessarily. " \
            "There's something nice about the carnal desire to destroy what's been created, after all."

EDIT_BRIEF = "A group of commands for modifications."
EDIT_HELP = "You tell me to change a thing. I change the thing. Kinda just depends on the thing I'm changing. Shrug. " \
            "I dunno what you want me to tell you--there isn't much more to it than the brief. It's cute that you're " \
            "spending time to hear all the things I have to say though. ^_^"

GET_BRIEF = "A group of commands for retrieving information."
GET_HELP = "Hehehe, the name for the string this is stored in is called 'GET_HELP'. Uh. Anyway. These commands are " \
           "designated for retrieving some type of information depending on the child command. This could include " \
           "information about your character's stats, inventory, metadata about your canon... lots of things."


# OLD Help Messages #


NEW_CAN_BRIEF = "'new canon' is a command to kick off a new RP."
NEW_CAN_HELP = "To Call: '" + COMM_PREFIX + COMM_NEW + " " + COMM_CANON + "'\n\n" \
               "Call anywhere within the server to have me walk you through the process of starting a new RP. " \
               "Ultimately this will create a new set of channels under a specific category named for said new RP. " \
               "Further, it automatically assigns the GM the role of GM and all other players to Observers roles. " \
               "Members added to the RP will become Players and through me can be granted privileges to call " \
               "certain commands--to make characters and start combat for instance. Otherwise, this sets the " \
               "stage for walking the GM through the metarules process wherein they choose the features I provide " \
               "that they wish to use for their RP."

DEL_CAN_BRIEF = "'delete canon' is a command to delete an RP and its associated channels and roles."
DEL_CAN_HELP = "To Call: '" + COMM_PREFIX + COMM_DEL + " " + COMM_CANON + "'\n\n" \
               "Call within the canon to ask all players if the canon should be deleted and the RP ended... " \
               "for the time being. If the vote goes through, I delete the channels, category and roles. I do, " \
               "however, hold onto player prefs, character stats, locations and other useful data that was generated " \
               "through the course of the RP. Just in case, you know. If you call new canon with the same name as " \
               "deleted canon, I will automatically link the data from the previous RP up with the newly created one. " \
               "You're welcome."

NEW_COM_BRIEF = "'new combat' is a command that begins a combat instance for you and other members participating."
NEW_COM_HELP = "To Call: '" + COMM_PREFIX + COMM_NEW + " " + COMM_COMBAT + "' within an RP command_room\n\n" \
               "When called, 'new combat' asks for each member participating in a combat instance. After confirming " \
               "that each member properly wants to participate/can participate in said combat, it sets up private " \
               "channels for each participant and opens the combat interface."

EDT_ESC_BRIEF = "'edit escape' is a command that changes the phrase to tell me that'll stop a command midway."
EDT_ESC_HELP = "To Call: '" + COMM_PREFIX + COMM_EDT + " " + COMM_ESC + "' anywhere.\n\n" \
               "When called, I'll ask ya for a phrase to replace the one that I typically use, '~' for escaping. " \
               "Try not to make this something you'd say often, because I'll definitely mix it up with something " \
               "you might want me to take as a command."

DEBUG_BRIEF = "'Debug' is a command that helps me test things. Don't worry about it."
DEBUG_HELP = "If I set this up properly, how did you ever get here...? Are you on my account? Spoopy."


# File Paths #
                                                            # Formatting String Args:

GUILDS_P = MODEL_FN + "\\" + GUILDS_FN                      # None
GUILD_P = GUILDS_P + "\\{}"                                 # Guild ID
CANONS_P = GUILD_P + "\\" + CANONS_FN                       # Guild ID
CANON_P = CANONS_P + "\\{}"                                 # Guild ID, Canon ID
KEYWORDS_P = CANON_P + "\\" + KEYWORDS_FN                   # Guild ID, Canon ID
KEYWORD_P = KEYWORDS_P + "\\{}.json"                        # Guild ID, Canon ID, Character Name
CHARACTERS_P = CANON_P + "\\" + CHARACTERS_FN               # Guild ID, Canon ID
CHARACTER_P = CHARACTERS_P + "\\{}.json"                    # Guild ID, Canon ID, Character Name
C_LOGS_P = CANON_P + "\\" + LOGS_FN                         # Guild ID, Canon ID
COMMAND_C_LOGS_P = C_LOGS_P + "\\" + COMMANDS_FN            # Guild ID, Canon ID
MEM_COMMAND_C_LOGS_P = COMMAND_C_LOGS_P + "\\{}"            # Guild ID, Canon ID, Member ID
MEM_COMMAND_C_LOG_P = MEM_COMMAND_C_LOGS_P + "\\{}.json"    # Guild ID, Canon ID, Member ID, (Command Name + Number)
META_P = CANON_P + "\\" + META_FN                           # Guild ID, Canon ID
IDS_P = META_P + "\\" + IDS_FN                              # Guild ID, Canon ID
EXCEPTIONS_P = META_P + "\\" + EXCEPTIONS_FN                # Guild ID, Canon ID
ROLES_P = META_P + "\\" + ROLES_FN                          # Guild ID, Canon ID
C_PLAYER_PREFS_P = CANON_P + "\\" + PLAYER_PREFS_FN         # Guild ID, Canon ID
C_PLAYER_PREF_P = C_PLAYER_PREFS_P + "\\{}.json"            # Guild ID, Canon ID, Member ID
ARCHIVES_P = CANONS_P + "\\" + ARCHIVES_FN                  # Guild ID,
ARCHIVE_P = ARCHIVES_P + "\\{}"                             # Guild ID, Canon Name
GENERAL_P = GUILD_P + "\\" + GENERAL_FN                     # Guild ID
G_PLAYER_PREFS_P = GENERAL_P + "\\" + PLAYER_PREFS_FN       # Guild ID
G_PLAYER_PREF_P = G_PLAYER_PREFS_P + "\\{}.json"            # Guild ID, Member ID
G_LOGS_P = GENERAL_P + "\\" + LOGS_FN                       # Guild ID
COMMAND_G_LOGS_P = G_LOGS_P + "\\" + COMMANDS_FN            # Guild ID
MEM_COMMAND_G_LOGS_P = COMMAND_G_LOGS_P + "\\{}"            # Guild ID, Member ID
MEM_COMMAND_G_LOG_P = MEM_COMMAND_G_LOGS_P + "\\{}.json"    # Guild ID, Member ID, (Command Name + Number)


# Other #


WS = [' ', '_', '-']


# Methods #


def bold(frmt):
    """Formats a string into a bold string"""
    return "**" + frmt + "**"


def itlc(frmt):
    """Formats a string into a italicized string"""
    return "_" + frmt + "_"


def skill_roll_string(mod_r, mod_v, dice_pool, base_pool, purpose, norm_stat_types, stats, successes):
    """Formats a skill roll final string."""
    if len(mod_r) > 0:
        mod_s = "Modifiers: "
        for i in range(len(mod_r)):
            if i < len(mod_r) - 1:
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

    final_string = \
        "> " + purpose + " (" + (norm_stat_types[0].title() if len(stats) == 1
                                 else norm_stat_types[0].title() + " + " + norm_stat_types[1].title()) + ")\n" \
        + "> " + mod_s + '\n' \
        + "> " + pool_s + '\n' \
        + "> " + successes

    return final_string


def rand_slack():
    """Returns a random slack off message."""
    return random.choice(ALL_SLACK)


# Snark #


YOUR_FUNERAL = "Your funeral."
UH = "...I see my name? You called but uh. I don't know what you want me to do."
A_SO = "\n\n...back to watching anime."
B_SO = "Now, time to recalibrate the canons."
C_SO = "Now, if you'll excuse me, I'm going to toy with character stats. Promise I won't change much. ;>"
D_SO = "Now buzz off. I've got 'important' things to get to. ...I'm just messing with you, I've got nothing but time."
E_SO = "But, uh, come back when you have something interesting for me to do, 'kay?"
F_SO = "Well, another day, another five-billion commands to handle."
G_SO = "\n\n...man, I live the good life. Underworked and overpaid. Just how I like it."
H_SO = "Okidoke. Seems like my work here is done."
I_SO = "Glad that's over. Now where was I on that cosplay..."
J_SO = "Was that it? Couldn't you have done that yourself? \n\nHaha, just kidding. I know ya'll are just _helpless_ " \
       " without me. ;>"
K_SO = "Yawn."
L_SO = "Time to find de wae."
M_SO = "Hey, you know I don't say this often but... thanks for letting me do my job. I joke... but I appreciate it. " \
       "^//^"
N_SO = "Manga calls!"
ALL_SLACK = [A_SO, B_SO, C_SO, D_SO, E_SO, F_SO, G_SO, H_SO, I_SO, J_SO, K_SO, L_SO, M_SO, N_SO]
