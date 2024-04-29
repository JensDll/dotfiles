from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Mapping, Protocol, Sequence

import gdb
from gdbdash.utils import GdbBool, GdbInt

from .command import CommandProtocol

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
Options = Mapping[str, Any]

class ConfigurableProtocol(CommandProtocol, Protocol):
    options: Options

class Configurable(metaclass=ABCMeta):
    def __init__(self, /, **kwargs) -> None: ...
    @cached_property
    @abstractmethod
    def options(self) -> Options: ...
