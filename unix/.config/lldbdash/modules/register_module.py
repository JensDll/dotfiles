import os
import typing

import lldb
import lldbdash.commands
from lldbdash.common import Output

from .on_change_output import on_change_output


class RegisterModule:
    Settings = typing.TypedDict(
        "Settings",
        {
            "show-32": lldbdash.commands.BoolCommand,
            "show-decimal": lldbdash.commands.BoolCommand,
            "show-segment": lldbdash.commands.BoolCommand,
            "show-eflags": lldbdash.commands.BoolCommand,
            "show-mxcsr": lldbdash.commands.BoolCommand,
            "show-vector": lldbdash.commands.BoolCommand,
            "output": lldbdash.commands.StrCommand,
        },
    )

    name = "register"

    settings: Settings = {
        "show-32": lldbdash.commands.BoolCommand(
            True, help="Visibility of general purpose registers 32-bit version"
        ),
        "show-decimal": lldbdash.commands.BoolCommand(
            True, help="Visibility of general purpose registers decimal value"
        ),
        "show-segment": lldbdash.commands.BoolCommand(
            True, help="Visibility of segment registers"
        ),
        "show-eflags": lldbdash.commands.BoolCommand(
            True, help="Visibility of eflags register"
        ),
        "show-mxcsr": lldbdash.commands.BoolCommand(
            True, help="Visibility of mxcsr register"
        ),
        "show-vector": lldbdash.commands.BoolCommand(
            True, help="Visibility of vector registers"
        ),
        "output": lldbdash.commands.StrCommand(
            "0",
            help="The render location of the register module.",
            on_change=on_change_output,
        ),
    }

    enabled = lldbdash.commands.ToggleCommand(
        True,
        enable_help="Enable the register module",
        disable_help="Disable the register module",
    )

    @staticmethod
    def render(size: os.terminal_size, exe_ctx: lldb.SBExecutionContext, out: Output):
        out.Print("REGISTERS\n")
