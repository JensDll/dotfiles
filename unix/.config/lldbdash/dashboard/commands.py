import json
import pathlib

import lldb

from .apply_config import apply_config
from .dashboard import Dashboard


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

        Dashboard.instance.handle_stop(exe_ctx, result)

    def get_short_help(self):
        return "Print the dashboard."

    def get_long_help(self):
        return None


class DumpCommand:
    def __init__(self, debugger: lldb.SBDebugger, internal_dict: dict):
        pass

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject,
    ):
        values = {
            "enabled": Dashboard.enabled.value,
            "settings": {
                name: option.value for name, option in Dashboard.get_settings().items()
            },
            "modules": {
                module.name: {
                    "enabled": module.enabled.value,
                    "settings": {
                        name: option.value for name, option in module.settings.items()
                    },
                }
                for module in Dashboard.modules
            },
        }

        with open(Dashboard.settings["config-file"].value, "w") as f:
            json.dump(values, f, indent=2)

    def get_short_help(self):
        return "Dump the current dashboard configuration to the config file."

    def get_long_help(self):
        return None


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


def is_running(exe_ctx: lldb.SBExecutionContext):
    state: int = exe_ctx.GetProcess().GetState()
    return Dashboard.instance and (
        state == lldb.eStateStopped or state == lldb.eStateCrashed
    )
