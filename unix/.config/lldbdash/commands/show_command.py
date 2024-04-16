import typing

import lldb

from .pure_command import PureCommand

if typing.TYPE_CHECKING:
    from .command import Command


class ShowCommand(PureCommand):
    def __init__(
        self,
        command,  # type: Command
        format: str,
        help: typing.Optional[str] = None,
        long_help: typing.Optional[str] = None,
    ):
        class Handle:
            def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
                pass

            def __call__(
                _self,
                _debugger: lldb.SBDebugger,
                _command: str,
                _exe_ctx: lldb.SBExecutionContext,
                _result: lldb.SBCommandReturnObject,
            ):
                _result.Print(f"{format.format(command.value)}\n")

            def get_short_help(self):
                return help

            def get_long_help(self):
                return long_help

        super().__init__(Handle)
