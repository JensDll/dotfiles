import typing

import lldb
from lldbdash.commands import PureCommand
from lldbdash.dashboard import get_size, is_running

if typing.TYPE_CHECKING:
    from lldbdash.modules import Module


class PrintCommand(PureCommand):
    def __init__(
        self,
        module: "Module",
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
                if not is_running(_exe_ctx):
                    _result.SetError("Dashboard is not running")
                    return
                size = get_size()
                module.render(size, _exe_ctx, _result)

            def get_short_help(self):
                return help

            def get_long_help(self):
                return long_help

        super().__init__(Handle)
