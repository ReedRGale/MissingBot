# ----------- Script by ReedRGale ----------- #
# Constant values used in the scripts. #


# Imports #


import discord


# Values #


SUCCESS_VALUES = 4
FAILURE_VALUES = 6
DICE_SIZE = 10

rooms = 0
rel_canon = ""  # TODO: Make this different per character / make this persist per person.
command_prefix = "~dd"
escape_value = "~"  # TODO: change this value and see if it still works.
focused_character = {}  # TODO: Deprecate this. It might be dangerous if multiple players change the focused character.

client = discord.Client()
app_token = "MzUzMTEzODg4Nzg0NjQ2MTQ0.DIunqw.tTJF2f3cDXSYXOcMdXMCETDqrLA"
