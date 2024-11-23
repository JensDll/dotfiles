import pathlib

import lldb

from .apply_config import apply_config
from .dashboard import Dashboard


class LoadCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
        pass

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        path = pathlib.Path.cwd() / Dashboard.settings["config-file"].value

        if not path.is_file():
            result.SetError(f"Config file not found: {path}")
            return

        apply_config(path, Dashboard.instance)

    def get_short_help(self):
        return "Load the dashboard configuration from the config file."

    def get_long_help(self):
        return None
