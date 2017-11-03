# ----------- Script by ReedRGale ----------- #
# Enums to denote special types. #


from enum import Enum


class UserType(Enum):
    observer = 0
    player = 1
    gm = 2

    def __str__(self):
        return self.name
