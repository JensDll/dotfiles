from dataclasses import dataclass
from typing import Sequence

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.utils import GdbBool, GdbInt


@dataclass
class BoolOption:
    doc: str
    value: GdbBool = GdbBool()
    choices: Sequence[str] = GdbBool.CHOICES

    def __str__(self):
        return str(self.value)


@dataclass
class IntOption:
    doc: str
    value: GdbInt = GdbInt()
    choices: int = gdb.COMPLETE_NONE

    def __str__(self):
        return str(self.value)


@dataclass
class StrOption:
    doc: str
    value: str
    choices: int = gdb.COMPLETE_NONE

    def __str__(self):
        return self.value
