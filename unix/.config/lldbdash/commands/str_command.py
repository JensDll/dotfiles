import shlex
import typing

import lldb

from .command import Command, OnChange, default_on_change


class StrCommand(Command[str]):
    def __init__(
        self,
        initial_value: str,
        help: typing.Optional[str] = None,
        long_help: typing.Optional[str] = None,
        show_format: str = "The current value is {}",
        show_help: typing.Optional[str] = None,
        show_long_help: typing.Optional[str] = None,
        on_change: OnChange = default_on_change,
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
                args = shlex.split(_command)

                if len(args) != 1:
                    _result.SetError(
                        f"Command expects exactly one argument but {len(args)} were given."
                    )
                    return

                self.set_value(args[0])

            def get_short_help(self):
                return help

            def get_long_help(self):
                return long_help

        super().__init__(
            initial_value,
            Handle,
            show_format=show_format,
            show_help=show_help,
            show_long_help=show_long_help,
            on_change=on_change,
        )
