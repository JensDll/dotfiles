import lldb

from .dashboard import Dashboard, is_running


class PrintCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
        pass

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        if not is_running(exe_ctx):
            result.SetError("Dashboard is not running")
            return
        Dashboard.instance.print(exe_ctx, result)

    def get_short_help(self):
        return "Print the dashboard."

    def get_long_help(self):
        return None
