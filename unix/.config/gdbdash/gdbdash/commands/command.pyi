from typing import Protocol

import gdb

class CommandProtocol(Protocol):
    command: gdb.Command
    command_name: str
    def dont_repeat(self) -> None: ...
    def invoke(self, arg: str, from_tty: bool) -> None: ...
    def complete(self, text: str, word: str) -> None: ...
    def write(self, message: str, fileno: int) -> None: ...
    def stdout(self, message: str) -> None: ...
    def stderr(self, message: str) -> None: ...

class Command:
    command: gdb.Command
    command_name: str
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
    def complete(self, text: str, word: str) -> object: ...
    def write(self, message: str, fileno: int) -> None: ...
    def stdout(self, message: str) -> None: ...
    def stderr(self, message: str) -> None: ...
