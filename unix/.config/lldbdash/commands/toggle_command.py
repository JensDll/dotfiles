import typing

import lldb

from .command import Command


class ToggleCommand(Command[bool]):
    def __init__(
        self,
        initial_value: bool,
        enable_help: typing.Optional[str] = None,
        enable_long_help: typing.Optional[str] = None,
        disable_help: typing.Optional[str] = None,
        disable_long_help: typing.Optional[str] = None,
    ):
        class Enable:
            def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
                pass

            def __call__(
                _self,
                debugger: lldb.SBDebugger,
                command: str,
                exe_ctx: lldb.SBExecutionContext,
                result: lldb.SBCommandReturnObject,
            ):
                self.prev_value = self.value
                self.value = True

            def get_short_help(self):
                return enable_help

            def get_long_help(self):
                return enable_long_help

        class Disable:
            def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
                pass

            def __call__(
                _self,
                debugger: lldb.SBDebugger,
                command: str,
                exe_ctx: lldb.SBExecutionContext,
                result: lldb.SBCommandReturnObject,
            ):
                self.prev_value = self.value
                self.value = False

            def get_short_help(self):
                return disable_help

            def get_long_help(self):
                return disable_long_help

        super().__init__(initial_value, Enable, Disable)

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return self.value
