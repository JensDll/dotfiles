import typing

import lldb

from .command import Command, OnChange, default_on_change


class ToggleCommand(Command[bool]):
    def __init__(
        self,
        initial_value: bool,
        enable_help: typing.Optional[str] = None,
        enable_long_help: typing.Optional[str] = None,
        disable_help: typing.Optional[str] = None,
        disable_long_help: typing.Optional[str] = None,
        show_format: str = "The current value is {}",
        show_help: typing.Optional[str] = None,
        show_long_help: typing.Optional[str] = None,
        on_change: OnChange = default_on_change,
    ):
        class Enable:
            def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
                pass

            def __call__(
                _self,
                _debugger: lldb.SBDebugger,
                _command: str,
                _exe_ctx: lldb.SBExecutionContext,
                _result: lldb.SBCommandReturnObject,
            ):
                self.set_value(True)

            def get_short_help(self):
                return enable_help

            def get_long_help(self):
                return enable_long_help

        class Disable:
            def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
                pass

            def __call__(
                _self,
                _debugger: lldb.SBDebugger,
                _command: str,
                _exe_ctx: lldb.SBExecutionContext,
                _result: lldb.SBCommandReturnObject,
            ):
                self.set_value(False)

            def get_short_help(self):
                return disable_help

            def get_long_help(self):
                return disable_long_help

        super().__init__(
            initial_value,
            Enable,
            Disable,
            show_format=show_format,
            show_help=show_help,
            show_long_help=show_long_help,
            on_change=on_change,
        )

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return self.value
