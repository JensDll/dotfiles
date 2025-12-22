import json

import lldb

from .dashboard import Dashboard


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
            "settings": {name: option.value for name, option in Dashboard.get_settings().items()},
            "modules": {
                module.name: {
                    "enabled": module.enabled.value,
                    "settings": {name: option.value for name, option in module.settings.items()},
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
