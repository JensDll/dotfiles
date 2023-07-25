from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Sequence

import gdb  # pyright: ignore [reportMissingModuleSource]

from . import DashboardModules
from .utils import FileDescriptorOrPath, GdbBool, GdbInt

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

class Command:
    def __init__(
        self,
        /,
        command_name: str,
        command_class: int,
        command_completer_class: int | None = None,
        command_prefix: bool = False,
        command_doc: str | None = None,
        **kwargs,
    ): ...
    def dont_repeat(self) -> None: ...
    def invoke(self, arg: str, from_tty: bool) -> None: ...
    def complete(self, text: str, word: str) -> None: ...
    def write(self, message: str, fileno: int) -> None: ...
    def stdout(self, message: str) -> None: ...
    def stderr(self, message: str) -> None: ...

class Configurable(metaclass=ABCMeta):
    def __init__(self, /, **kwargs) -> None: ...
    @property
    @abstractmethod
    def options(self) -> Options: ...

class Togglable(metaclass=ABCMeta):
    enabled: bool
    def __init__(self, /, **kwargs) -> None: ...
    @abstractmethod
    def enable(self) -> None: ...
    @abstractmethod
    def disable(self) -> None: ...

class Outputable:
    dashboard_modules: DashboardModules
    output: FileDescriptorOrPath
    def on_output_changed(self, old_output: FileDescriptorOrPath) -> None: ...
