import json
import shutil
import typing
from os import terminal_size

import lldb
import lldbdash.commands
import lldbdash.modules

from .common import Output, file_streams, is_file


class Dashboard:
    Settings = typing.TypedDict(
        "Settings",
        {"config-file": lldbdash.commands.StrCommand},
    )

    instance: typing.ClassVar["Dashboard"]
    modules: typing.ClassVar[list[lldbdash.modules.Module]]
    settings: typing.ClassVar[Settings] = {
        "config-file": lldbdash.commands.StrCommand(
            "lldbdash.json", help="The config file name."
        )
    }
    enabled: typing.ClassVar[lldbdash.commands.ToggleCommand]

    def __init__(
        self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, dict: dict
    ):
        self.size = shutil.get_terminal_size((160, 24))
        Dashboard.instance = self

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, output: Output):
        for module in Dashboard.modules:
            out = output
            module_output = module.settings["output"].value
            if is_file(module_output):
                out = file_streams[module_output]["stream"]
            out.Print(f"--------- {module.name} ----------------------------------\n")
            module.render(self.size, exe_ctx, out)


def is_running(exe_ctx: lldb.SBExecutionContext):
    state: int = exe_ctx.GetProcess().GetState()
    return Dashboard.instance and (
        state == lldb.eStateStopped or state == lldb.eStateCrashed
    )


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
        with open(Dashboard.settings["config-file"].value) as f:
            json_config = json.load(f)

        Dashboard.enabled.set_value(json_config["enabled"])

        for name, json_module in json_config["modules"].items():
            module: lldbdash.modules.Module = next(
                filter(lambda m: m.name == name, Dashboard.modules)
            )
            module.enabled.set_value(json_module["enabled"])
            for name, value in json_module["settings"].items():
                module.settings[name].set_value(value)

    def get_short_help(self):
        return "Load the dashboard configuration from the config file."

    def get_long_help(self):
        return None
