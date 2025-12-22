import typing

import lldb

from lldbdash.common import Settings

from .pure_command import PureCommand


class ListSettingsCommand(PureCommand):
    def __init__(self, settings: Settings, help: typing.Optional[str] = None):
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
                for key, value in settings.items():
                    _result.Print(f"{key}: {repr(value.value)}\n")

            def get_short_help(self):
                return help

            def get_long_help(self):
                return None

        super().__init__(Handle)
