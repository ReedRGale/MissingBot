# ----------- Script by ReedRGale ----------- #
# String constants used in the scripts. #


# Imports #


import random


# Informative Messages #


INF_DONE = "The thing you asked for should be done now."
INF_NAUGHT = "Nothing to see here."
INF_BROKEN = "I know. It's broken. I'll get to it when I get to it."
INF_CHANNELS_MADE = "Alright bud, I think things are set in place. Your private combat channel is made " \
                    "and should be called: "
INF_CANON_MADE = "All the paperwork is in order. Enjoy the new world, I guess."
INF_CANON_SET = "Well, here you are. Enjoy your stay or something."
INF_NOT_GM = "Wise choice. I'll let that jerk know you don't want any part of this nonsense."
INF_DENIED_GM = "They made the smart choice and chose not to be GM. Call me again when you have someone for the job."

SAVED = "Databank updated, for whatever reason it needed updating!"
ESCAPE = "I'll escape the command, but just because you asked nicely. ;>"


def rand_slack():
    """Returns a random slack off message."""
    return random.choice(ALL_SLACK)


# Help Messages #

NN_BRIEF = "'NewCanon' is a command to kick off a new RP."
NN_HELP = "To Call: '~dd newcanon'\n\n" \
          "Call anywhere within the server to have me walk you through the process of starting a new RP. Ultimately " \
          "this will create a new set of channels under a specific category named for said new RP. Further, it " \
          "automatically assigns the GM the role of GM and all other players to Observers roles. Members added to " \
          "the RP will become Players and through me can be granted privileges to call certain commands--to make " \
          "characters and start combat for instance. Otherwise, this sets the stage for walking the GM through the " \
          "metarules process wherein they choose the features I provide that they wish to use for their RP."

FT_BRIEF = "'Forecast' is a command that should give you an idea of how likely " \
           "getting any particular amount of successes will be."
FT_HELP = "To Call: '~dd forecast [forecast] [# of dice in pool]' \n\n" \
          "Forecast gives an accurate measurement, using NWoD skill-check rules, of the likelihood that a particular" \
          "amount of successes will occur--called the forecast--in a particular dice pool--that is, the total number " \
          "of dice that are currently being rolled."

NR_BRIEF = "'NewCharacter' is a command that allows you to add another character to the canon."
NR_HELP = "To Call: '~dd newcharacter' within an RP command_room\n\n" \
          "When called, 'NewCharacter' walks the user through the process of making a new character following the" \
          "meta decided upon for the RP. Each step records a single important field for the character. Unless given" \
          "permission, this can only be called by the GM. This command is not callable until the meta is decided upon."

LR_BRIEF = "'ListCharacters' is a command that shows you all recorded characters in the canon."
LR_HELP = "To Call: '~dd listcharacters' within an RP command_room\n\n" \
          "When called, prints a list of each character currently registered in the RP."

SL_BRIEF = "'Skillroll' is a command that walks you through rolling dice for a skill roll."
SL_HELP = "To Call: '~dd skillroll' within an RP command_room\n\n" \
          "Skillroll asks all the proper questions to make a NWoD Skill Roll, then properly formats the string for " \
          "posting in a forum or in the middle of a channel message."

NT_BRIEF = "'NewCombat' is a command that begins a combat instance for you and other members participating."
NT_HELP = "To Call: '~dd skillroll' within an RP command_room\n\n" \
          "When called, NewCombat asks for each member participating in a combat instance. After confirming that " \
          "each member properly wants to participate/can participate in said combat, it sets up private channels " \
          "for each participant and opens the combat interface."

HP_BRIEF = "'Help' is a standard help command. By calling '~dd help [item]' " \
           "on any command or all-caps word, you can get a small piece on that item."
HP_HELP = "Good work. That is exactly how you check the detailed help docs of a command."

DB_BRIEF = "'Debug' is a command that helps me test things. Don't worry about it."
DB_HELP = "If I set this up properly, how did you ever get here...? Are you on my account? Spoopy."


# Request Messages #


REQ_STATS = "Which stats are related to this roll? Separate with commas. \n"
REQ_ACTIVE_CHARACTER = "Which character is rolling? \n"
REQ_CHARACTER = "Please provide a "
REQ_MOD_REASON = "What's one factor affecting this roll?"
REQ_ROLL_PURPOSE = "What's this skill roll for?"
REQ_MOD_AMOUNT = "By how many dice should this affect the roll? (i.e. -3, 4, 1, 2, etc...)"
REQ_CANON = "Alright... so what canon are we working with today?"
REQ_NEW_CANON = "So, what'cha wanna call this new story-world?"
REQ_USER_COMBAT = "Now, which users are taking part in this 'glorious brawl?' You know the drill, " \
                  "list them all with at tags (@) and separate them with commas. Ah, do note that the GM " \
                  "is automatically included. No need to worry there. \n\n " \
                  "Ex: @DJ Dante , @ReedRGale"
REQ_PLAYER = "So, which player is gonna to be using this character? Remember to use their taggable name. You know, " \
             "the one with the '@' in it?"
REQ_USER_GM = "Okay, so who's gonna be running this show? If it's you, tag yourself. Otherwise, tag someone else."
REQ_REL_CANON = "Alright, so what canon is your poison today?"


# Confirmations #


ASK_IF_MODS = "Are there modifications to this roll? " \
             "(i.e. Its dark; You made a torch to light the way; etc...)"
ASK_IF_MORE_MODS = "Any more modifications to make?"
ASK_IF_FIGHT = "So, someone challenged you to combat. You gonna make that fight happen in canon?"
ASK_IF_GM = "Are you really sure you want to do this? Managing an RP is hard and you might have just been " \
            "nominated for something you don't want to do. If so, just tell me 'no.' If not... well, your funeral. " \
            "You know what they say about funerals though. Can't spell it without 'fun.' \n\n" \
            "Anyway. What'll it be? Will you be this canon's god (world/RP)?"


# Error Messages #

ERR_REPEAT_1 = "Let's try that again."
ERR_REPEAT_2 = "Try again. With feeling this time."

ERR_EXTRA_ARGS = "Whoa there pardner. That's a lot of arguments. Try to keep it to around "
ERR_NOT_ENOUGH_ARGS = "Hey. Buddy. You need at least this many arguments to use this command: "
ERR_PLAYER_EXIST = "Yo. So... uh... don't try to like... take this character's identity. K? They already exist. " \
                   "Let 'em be."
ERR_PLAYER_NONEXIST = "Yo. So... uh... I don't know how to put this nicely. But... that player doesn't... exist? Yeah."
ERR_CANON_NONEXIST = "Okay so... these worlds aren't real, but this one you just wrote exists less than the other " \
                     "worlds that don't exist. That is, I don't have it in my records."
ERR_ONLY_ONE_GM = "Alright, let's start with just one GM. Simplifies things for now. Later you can add multiple GMs." \
                  "But for now... let's keep it simple."
ERR_CHANNEL_NOT_IN_CANON = "This channel isn't in a canon. Try calling this command somewhere it would, y'know, _work_."
ERR_INV_ARG = "Sorry, don't know that keyword "
ERR_REPEAT_ARG = "You've already used the keyword "
ERR_INV_FORM = "Invalid. Once more, with feeling this time."
ERR_STAT_LT_ZERO = "A stat can't be less than 0. And, let's be fair, do you really want it to be?"
ERR_STAT_GT_FIFT = "A stat can't be greater than 15. And that's already obnoxiously high as it is."
ERR_NOT_YES_OR_NO = "Sorry, that doesn't look affirmative or negatory, boss. If worst comes to worst, " \
                    "don't be creative. A simple 'yes' or 'no' would suffice. So once more. With feeling this time."
ERR_CANON_EXISTS = "This world is kind of already a thing. Don't like, get all up in its biz' ya dig?"
ERR_NOT_IN_RP = "Hey. This person is just an observer here. What're ya tryin to pull?"
ERR_NOT_IN_GUILD = "Okay so maybe you really like that person. But they aren't here. I can't work with people that " \
                   "aren't here."


# Other #


CHARACTERS_FN = "characters"
META_FN = "meta"
LOGS_FN = "logs"
CANONS_FN = "canons"
PLAYER_PREFS_FN = "player_prefs"
ROLES_FN = "roles.json"
EXCEPTIONS_FN = "command_exceptions.json"
SUCCESS = "S - "
FAILURE = "F - "
AGAIN = "A - "


# Snark #


YOUR_FUNERAL = "Your funeral."
UH = "...I see my name? You called but uh. I don't know what you want me to do. "
A_SO = "\n\n...back to watching anime."
B_SO = "Now, time to recalibrate the canons."
C_SO = "Now, if you'll excuse me, I'm going to toy with your character's stats. Promise I won't change them much. ;>"
D_SO = "Now buzz off. I've got 'important' things to get to. ...I'm just messing with you, I've got nothing but time."
E_SO = "But, uh, come back when you have something interesting for me to do, 'kay?"
F_SO = "Well, another day, another five-billion commands to handle."
G_SO = "\n\n...man, I live the good life. Bossed around, yet underworked and overpaid. Just how I like it."
ALL_SLACK = [A_SO, B_SO, C_SO, D_SO, E_SO, F_SO, G_SO]
