import os
import typing

import lldb
import lldbdash.commands
from lldbdash.common import RESET_COLOR, Output, batched, not_none
from lldbdash.dashboard import Dashboard as D
from lldbdash.register_lookup import Register, RegisterLookup, get_gp_register_set

from .on_change_output import on_change_output

if typing.TYPE_CHECKING:
    ModuleSettings = typing.TypedDict(
        "ModuleSettings",
        {
            "show-decimal": lldbdash.commands.BoolCommand,
            "show-segment": lldbdash.commands.BoolCommand,
            "show-eflags": lldbdash.commands.BoolCommand,
            "show-mxcsr": lldbdash.commands.BoolCommand,
            "show-vector": lldbdash.commands.BoolCommand,
            "output": lldbdash.commands.StrCommand,
        },
    )


gp_names = [
    "rax",
    "rbx",
    "rcx",
    "rdx",
    "rdi",
    "rsi",
    "rbp",
    "rsp",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "r13",
    "r14",
    "r15",
]


class RegisterModule:
    name = "register"
    settings: "ModuleSettings" = {
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
        frame: lldb.SBFrame = exe_ctx.GetFrame()

        lookup = RegisterLookup.new_or_cached(frame)

        gp_reg_set = get_gp_register_set(frame)
        gp_regs = filter(
            not_none,
            [
                lookup.read_register(gp_reg_set, "rax"),
                lookup.read_register(gp_reg_set, "rbx"),
                lookup.read_register(gp_reg_set, "rcx"),
                lookup.read_register(gp_reg_set, "rdx"),
                lookup.read_register(gp_reg_set, "rdi"),
                lookup.read_register(gp_reg_set, "rsi"),
                lookup.read_register(gp_reg_set, "rbp"),
                lookup.read_register(gp_reg_set, "rsp"),
                lookup.read_register(gp_reg_set, "r8"),
                lookup.read_register(gp_reg_set, "r9"),
                lookup.read_register(gp_reg_set, "r10"),
                lookup.read_register(gp_reg_set, "r11"),
                lookup.read_register(gp_reg_set, "r12"),
                lookup.read_register(gp_reg_set, "r13"),
                lookup.read_register(gp_reg_set, "r14"),
                lookup.read_register(gp_reg_set, "r15"),
            ],
        )

        per_row = size.columns // 40

        for batch in batched(gp_regs, per_row):
            for i in range(len(batch) - 1):
                write_hex(out, batch[i])
                out.write("  ")
            write_hex(out, batch[-1])
            out.write("\n")
            if RegisterModule.settings["show-decimal"]:
                for i in range(len(batch) - 1):
                    write_decimal(out, batch[i])
                    out.write("  ")
                write_decimal(out, batch[-1])
                out.write("\n")


def write_hex(out: Output, reg: Register):
    out.write(
        D.settings["text-highlight"].value
        if reg.changed
        else D.settings["text-secondary"].value
    )
    out.write(f"{reg.name:>18}")
    out.write(RESET_COLOR)
    out.write(" ")
    out.write(reg.hex_str)


def write_decimal(out: Output, reg: Register):
    out.write(" " * 17)
    out.write(
        D.settings["text-highlight"].value
        if reg.changed
        else D.settings["text-secondary"].value
    )
    out.write("=")
    out.write(RESET_COLOR)
    out.write(f" {reg.int:>{len(reg.hex_str)}}")
