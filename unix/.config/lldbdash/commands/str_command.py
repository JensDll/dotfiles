import shlex
import typing

import lldb

from .command import Command


class StrCommand(Command[str]):
    def __init__(
        self,
        initial_value: str,
        help: typing.Optional[str] = None,
        long_help: typing.Optional[str] = None,
    ):
        class Handle:
            def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
                pass

            def __call__(
                _self,
                debugger: lldb.SBDebugger,
                command: str,
                exe_ctx: lldb.SBExecutionContext,
                result: lldb.SBCommandReturnObject,
            ):
                args = shlex.split(command)

                if len(args) != 1:
                    result.SetError(
                        f"Command expects exactly one argument but {len(args)} were given."
                    )
                    return

                self.set_value(args[0])

            def get_short_help(self):
                return help

            def get_long_help(self):
                return long_help

        super().__init__(initial_value, Handle)

    def __str__(self):
        return self.value
