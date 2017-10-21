# ----------- Script by ReedRGale ----------- #
# String constants used in the scripts. #


# Help Messages #


FC_HELP = "'Forecast' is a command that should give you an idea of how likely " \
          "getting any particular amount of successes will be."
NR_HELP = "'NewActor' is a command that allows you to add another character (actor) to the canon."
LR_HELP = "'ListActors' is a command that shows you all recorded actors in the canon."
SL_HELP = "'Skillroll' is a command that walks you through rolling dice for a skill roll."
DB_HELP = "'Debug' is a command that helps me test things. Don't worry about it."


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
SAVED = "Databank updated, for whatever reason it needed updating!"


# Error Messages #


EXTRA_ARGS = "It appears you attempted to use more than the required args. This command wants "
INV_ARG = "I don't recognize the keyword "
REPEAT_ARG = "You've already used the keyword "
INV_FORM = "It seems invalid. Try again."
LT_ZERO = "A stat can't be less than 0. And, let's be fair, do you really want it to be?"
GT_FIFT = "A stat can't be greater than 15. And that's already obnoxiously high as it is."
REPEAT = "Could you repeat the command?"
ESCAPE = "Escaping command..."


# Other #


SUCCESS = "S - "
FAILURE = "F - "
AGAIN = "A - "
