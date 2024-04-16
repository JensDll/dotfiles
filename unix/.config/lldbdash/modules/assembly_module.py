import os

import lldb
import lldbdash.commands

from .on_change_output import on_change_output


class AssemblyModule:
    settings = {}
    name = "assembly"
    output = lldbdash.commands.StrCommand(
        "0",
        help="The render location of the assembly module.",
        on_change=on_change_output,
    )
    enabled = lldbdash.commands.ToggleCommand(
        True,
        enable_help="Enable the assembly module",
        disable_help="Disable the assembly module",
    )

    @staticmethod
    def render(
        size: os.terminal_size, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream
    ):
        stream.Print("ASSEMBLY\n")
        stream.Print(f"OUTPUT = {AssemblyModule.output.value}\n")
