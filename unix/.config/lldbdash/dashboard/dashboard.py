import pathlib
import shutil
import typing

import lldb
import lldbdash.commands
from lldbdash.common import RESET_COLOR, Output, Settings, g_file_streams

from .apply_config import apply_config

if typing.TYPE_CHECKING:
    from os import terminal_size

    from lldbdash.modules import Module

    DashboardSettings = typing.TypedDict(
        "DashboardSettings",
        {
            "config-file": lldbdash.commands.StrCommand,
            "text-highlight": lldbdash.commands.StrCommand,
            "text-secondary": lldbdash.commands.StrCommand,
            "divider-fill-char": lldbdash.commands.StrCommand,
            "show-divider": lldbdash.commands.BoolCommand,
            "auto-apply-config": lldbdash.commands.BoolCommand,
            "output": lldbdash.commands.StrCommand,
        },
    )


def on_change_output(prev_output: str, output: str):
    for module in Dashboard.modules:
        module.settings["output"].set_value(output)


def is_running(exe_ctx: lldb.SBExecutionContext):
    state: int = exe_ctx.GetProcess().GetState()
    return Dashboard.instance and (
        state == lldb.eStateStopped or state == lldb.eStateCrashed
    )


def terminal_window_size():
    return shutil.get_terminal_size((160, 24))


class Dashboard:
    modules: typing.ClassVar[list["Module"]]
    instance: typing.ClassVar["Dashboard"]
    settings: typing.ClassVar["DashboardSettings"] = {
        "config-file": lldbdash.commands.StrCommand(
            "lldbdash.json", help="The config file name."
        ),
        "text-highlight": lldbdash.commands.StrCommand("\033[38;2;229;229;16m"),
        "text-secondary": lldbdash.commands.StrCommand("\033[38;2;114;114;110m"),
        "divider-fill-char": lldbdash.commands.StrCommand("─"),
        "show-divider": lldbdash.commands.BoolCommand(True),
        "auto-apply-config": lldbdash.commands.BoolCommand(
            True, help="Auto apply config changes when edited during debug session."
        ),
        "output": lldbdash.commands.StrCommand(
            "0",
            help="The render location of the dashboard.",
            on_change=on_change_output,
        ),
    }
    enabled: typing.ClassVar[lldbdash.commands.ToggleCommand]

    def __init__(
        self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, dict: dict
    ):
        self.config_modified_time = 0
        Dashboard.instance = self

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, out: Output):
        self.apply_config()
        if not Dashboard.enabled:
            return
        self.print_modules(exe_ctx, out)

    def print(self, exe_ctx: lldb.SBExecutionContext, out: Output):
        self.apply_config()
        self.print_modules(exe_ctx, out)

    def print_modules(self, exe_ctx: lldb.SBExecutionContext, out: Output):
        show_divider = Dashboard.settings["show-divider"].value
        size = terminal_window_size()
        for module in Dashboard.modules:
            output = out
            module_output = module.settings["output"].value
            if module_output != "0":
                output = g_file_streams[module_output]["stream"]
            if show_divider:
                self.print_divider(size, module, output)
            module.render(size, exe_ctx, output)

    def print_divider(self, size: "terminal_size", module: "Module", out: Output):
        fill_char = Dashboard.settings["divider-fill-char"].value

        before = fill_char * (size.columns >> 4)
        name = f" {module.name} "
        after = fill_char * (size.columns - len(before) - len(name))

        out.write(Dashboard.settings["text-secondary"].value)
        out.write(before)
        out.write(name)
        out.write(after)
        out.write(RESET_COLOR)
        out.write("\n")

    def apply_config(self):
        path = pathlib.Path.cwd() / Dashboard.settings["config-file"].value
        if Dashboard.settings["auto-apply-config"].value and path.is_file():
            config_modified_time = path.stat().st_mtime
            if config_modified_time > self.config_modified_time:
                self.config_modified_time = config_modified_time
                apply_config(path, self)

    @classmethod
    def get_settings(cls):
        return typing.cast(Settings, cls.settings)
