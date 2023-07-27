from dataclasses import dataclass
from typing import Mapping, Sequence

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.utils import GdbBool, GdbInt

@dataclass
class BoolOption:
    doc: str
    value: GdbBool = GdbBool()
    choices: Sequence[str] = GdbBool.CHOICES

@dataclass
class IntOption:
    doc: str
    value: GdbInt = GdbInt()
    choices: int = gdb.COMPLETE_NONE

@dataclass
class StrOption:
    doc: str
    value: str
    choices: int = gdb.COMPLETE_NONE

Option = BoolOption | IntOption | StrOption
Options = Mapping[str, Option]
