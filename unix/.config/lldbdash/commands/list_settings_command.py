import typing

import lldb

from .command import EmptyCommand


class ListSettingsCommand(EmptyCommand):
    def __init__(
        self,
        settings: dict,
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
                for key, value in settings.items():
                    result.Print(f"{key}: {value}\n")

            def get_short_help(self):
                return help

            def get_long_help(self):
                return long_help

        super().__init__(Handle)
