# ----------- Script by ReedRGale ----------- #
# String constants used in the scripts. #


# Imports #


import random


# TODO:  Make a random room name generator
# TODO:  Make a room-word submission command


# Informative Messages #


DONE_INFORM = "The thing you asked for should be done now."
NAUGHT_INFORM = "Nothing to see here."
BROKEN_INFORM = "I know. It's broken. I'll get to it when I get to it."


# Back to Slacking Off #

UH = "...I see my name? You called but uh. I don't know what you want me to do. "
A_SO = "...back to watching anime."
B_SO = "Now, time to recalibrate the canons."
C_SO = "If you'll excuse me, I'm going to toy with your character's stats. Promise I won't change them much. ;>"
D_SO = "Now buzz off. I've got 'important' things to get to. ...I'm just messing with you, I've got nothing but time."
E_SO = "Come back when you have something interesting for me to do."
ALL_SLACK = [A_SO, B_SO, C_SO, D_SO, E_SO]


def rand_slack():
    """Returns a random slack off message."""
    return random.choice(ALL_SLACK)


# Help Messages #


FC_HELP = "'Forecast' is a command that should give you an idea of how likely " \
          "getting any particular amount of successes will be."
NR_HELP = "'NewActor' is a command that allows you to add another character (actor) to the canon."
LR_HELP = "'ListActors' is a command that shows you all recorded actors in the canon."
SL_HELP = "'Skillroll' is a command that walks you through rolling dice for a skill roll."
DB_HELP = "'Debug' is a command that helps me test things. Don't worry about it."
RT_HELP = "'RegisterCombat' is a command that begins a combat instance for you and other members participating."


# Request Messages #


REQ_STATS = "Which stats are related to this roll? Separate with commas. \n"
REQ_ACTIVE_ACTOR = "Which character is rolling? \n"
REQ_ACTOR = "Please provide a "
REQ_MOD_REASON = "What's one factor affecting this roll?"
REQ_ROLL_PURPOSE = "What's this skill roll for?"
REQ_MOD_AMOUNT = "By how many dice should this affect the roll? (i.e. -3, 4, 1, 2, etc...)"
ASK_IF_MODS = "Are there modifications to this roll? " \
             "(i.e. Its dark; You made a torch to light the way; etc...)"
ASK_IF_MORE_MODS = "Any more modifications to make?"

REQ_CANON = "Alright... so what canon are we working with today?"
REQ_USER = "Now, which users are taking part in this 'glorious brawl?' You know the drill, " \
           "list them all with at tags (@) and separate them with commas. Ah, do note that the GM is automatically " \
           "included. No need to worry there. \n\n " \
           "Ex: @DJ Dante , @ReedRGale"
ASK_IF_FIGHT = "So, someone challenged you to combat. You gonna make that fight happen in canon?"

SAVED = "Databank updated, for whatever reason it needed updating!"


# Error Messages #


EXTRA_ARGS = "Whoa there pardner. That's a lot of arguments. Try to keep it to around "
NOT_ENOUGH_ARGS = "Hey. Buddy. You need at least this many arguments to use this command: "
PLAYER_NONEXIST = "Yo. So... uh... I don't know how to put this nicely. But... that player doesn't... exist? Yeah."
CANON_NONEXIST = "These worlds aren't real, but this one you just said exists less than the other " \
                 "worlds that don't exist. That is, I don't have it in my records."
INV_ARG = "Sorry, don't know that keyword "
REPEAT_ARG = "You've already used the keyword "
INV_FORM = "Invalid. Once more, with feeling this time."
LT_ZERO = "A stat can't be less than 0. And, let's be fair, do you really want it to be?"
GT_FIFT = "A stat can't be greater than 15. And that's already obnoxiously high as it is."
REPEAT = "Let's try that again."
ESCAPE = "I'll escape the command, but just because you asked nicely. ;>"
NOT_YES_OR_NO = "Sorry, that doesn't look affirmative or negatory, boss. If worst comes to worst, don't be creative. " \
                "A simple 'yes' or 'no' would suffice. So once more. With feeling this time."

# Informative #

INF_CHANNELS_MADE = "Alright bud, I think things are set in place. Your private combat channel is made " \
                    "and should be called: "


# Other #


SUCCESS = "S - "
FAILURE = "F - "
AGAIN = "A - "
