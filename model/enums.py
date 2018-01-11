# ----------- Script by ReedRGale ----------- #
# Enums to denote special types. #


from enum import Enum
from functools import total_ordering


@total_ordering
class UserType(Enum):
    OBSERVER = 0
    PLAYER = 1
    GM = 2

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented

    def __str__(self):
        return self.name


class TidyMode(Enum):
    STANDARD = 0
    WARNING = 1
    PROMPT = 2

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
