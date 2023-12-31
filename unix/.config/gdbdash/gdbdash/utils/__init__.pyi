from os import PathLike
from typing import Any, Callable, Final, Literal, Sequence, TypedDict

import gdb

RESET_COLOR: Literal["\033[0m"]
FONT_BOLD: Literal["\033[1m"]
FONT_UNDERLINE = Literal["\033[4m"]

StrOrBytesPath = str | bytes | PathLike[str] | PathLike[bytes]
FileDescriptorOrPath = int | StrOrBytesPath
WriteWrapper = Callable[[str], Any]

def complete(word: str, candidates: Sequence[str]) -> Sequence[str]: ...

class GdbBool:
    CHOICES: Final[Sequence[str]]
    def __init__(self, default: bool = False) -> None: ...
    def __set_name__(self, owner: Any, name: str) -> None: ...
    def __get__(self, instance: Any, owner: Any = None) -> bool: ...
    def __set__(self, instance: Any, value: Any) -> None: ...
    @staticmethod
    def to_python(value: str) -> bool: ...

class GdbInt:
    def __set_name__(self, owner: Any, name: str): ...
    def __get__(self, instance, owner=None) -> int: ...
    def __set__(self, instance, value) -> None: ...

class Instruction(TypedDict):
    addr: int
    length: int
    asm: str

def fetch_instructions(
    architecture: gdb.Architecture, start_pc: int, count: int = 1
) -> list[Instruction]: ...
def fetch_instructions_range(
    architecture: gdb.Architecture, start_pc: int, end_pc: int
) -> list[Instruction]: ...
def fetch_pc(frame: gdb.Frame) -> int: ...
