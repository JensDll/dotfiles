import os

import lldb
import lldbdash.commands


class AssemblyModule:
    settings = {}
    name = "assembly"
    output = lldbdash.commands.StrCommand(
        "0",
        help="The render location of the assembly module.",
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
