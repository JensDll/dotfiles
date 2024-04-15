import shlex
import typing

import lldb

from .command import Command


class BoolCommand(Command[bool]):
    def __init__(
        self,
        initial_value: bool,
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

                arg = args[0].lower()

                if arg == "true" or arg == "on" or arg == "1" or arg == "enable":
                    self.set_value(True)
                    return

                if arg == "false" or arg == "off" or arg == "0" or arg == "disable":
                    self.set_value(False)
                    return

                result.SetError(f"Invalid argument {arg} must be convertible to bool")

            def get_short_help(self):
                return help

            def get_long_help(self):
                return long_help

        super().__init__(initial_value, Handle)

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return self.value
