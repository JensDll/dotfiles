import os
import typing

import lldb
import lldbdash.commands
from lldbdash.common import FONT_UNDERLINE, RESET_COLOR, Output, batched
from lldbdash.dashboard import Dashboard as D
from lldbdash.register_lookup import (
    AvxRegister,
    GeneralPurposeRegister,
    MxcsrRegister,
    RegisterLookup,
    RflagsRegister,
    SegmentRegister,
    get_avx_reg_set,
    get_fp_reg_set,
    get_gp_reg_set,
)

from .on_change_output import on_change_output

if typing.TYPE_CHECKING:
    ModuleSettings = typing.TypedDict(
        "ModuleSettings",
        {
            "show-decimal": lldbdash.commands.BoolCommand,
            "show-segment": lldbdash.commands.BoolCommand,
            "show-rflags": lldbdash.commands.BoolCommand,
            "show-mxcsr": lldbdash.commands.BoolCommand,
            "show-vector": lldbdash.commands.BoolCommand,
            "output": lldbdash.commands.StrCommand,
        },
    )


class RegisterModule:
    name = "register"
    settings: "ModuleSettings" = {
        "show-decimal": lldbdash.commands.BoolCommand(
            True, help="Display general purpose registers decimal value."
        ),
        "show-segment": lldbdash.commands.BoolCommand(
            True, help="Display segment registers."
        ),
        "show-rflags": lldbdash.commands.BoolCommand(
            True, help="Display rflags register."
        ),
        "show-mxcsr": lldbdash.commands.BoolCommand(
            True, help="Display mxcsr register."
        ),
        "show-vector": lldbdash.commands.BoolCommand(
            True, help="Display vector registers."
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
        registers = RegisterLookup.new_or_cached(frame)

        gp_reg_set = get_gp_reg_set(frame)
        fp_reg_set = get_fp_reg_set(frame)
        avx_reg_set = get_avx_reg_set(frame)

        write_gp(
            out,
            [
                registers.read_gp(gp_reg_set, "rax"),
                registers.read_gp(gp_reg_set, "rbx"),
                registers.read_gp(gp_reg_set, "rcx"),
                registers.read_gp(gp_reg_set, "rdx"),
                registers.read_gp(gp_reg_set, "rdi"),
                registers.read_gp(gp_reg_set, "rsi"),
                registers.read_gp(gp_reg_set, "rbp"),
                registers.read_gp(gp_reg_set, "rsp"),
                registers.read_gp(gp_reg_set, "r8"),
                registers.read_gp(gp_reg_set, "r9"),
                registers.read_gp(gp_reg_set, "r10"),
                registers.read_gp(gp_reg_set, "r11"),
                registers.read_gp(gp_reg_set, "r12"),
                registers.read_gp(gp_reg_set, "r13"),
                registers.read_gp(gp_reg_set, "r14"),
                registers.read_gp(gp_reg_set, "r15"),
            ],
            size.columns // 40,
        )

        if RegisterModule.settings["show-segment"]:
            write_segment(
                out,
                [
                    registers.read_segment(gp_reg_set, "cs"),
                    registers.read_segment(gp_reg_set, "ss"),
                    registers.read_segment(gp_reg_set, "ds"),
                    registers.read_segment(gp_reg_set, "es"),
                    registers.read_segment(gp_reg_set, "fs"),
                    registers.read_segment(gp_reg_set, "gs"),
                ],
            )

        if RegisterModule.settings["show-rflags"]:
            write_rflags(out, registers.read_rflags(gp_reg_set))

        if RegisterModule.settings["show-vector"]:
            write_avx(
                out,
                [
                    registers.read_avx(avx_reg_set, fp_reg_set, f"ymm{i}")
                    for i in range(16)
                ],
            )

        if RegisterModule.settings["show-mxcsr"]:
            write_mxcsr(out, registers.read_mxcsr(fp_reg_set))


def write_gp(out: Output, regs: list[GeneralPurposeRegister], per_row: int):
    show_decimal = RegisterModule.settings["show-decimal"].value
    for batch in batched(regs, per_row):
        for i in range(len(batch) - 1):
            write_gp_hex(out, batch[i])
            out.write("  ")
        write_gp_hex(out, batch[-1])
        out.write("\n")
        if show_decimal:
            for i in range(len(batch) - 1):
                write_gp_decimal(out, batch[i])
                out.write("  ")
            write_gp_decimal(out, batch[-1])
            out.write("\n")


def write_gp_hex(out: Output, reg: GeneralPurposeRegister):
    out.write(
        D.settings["text-highlight"].value
        if reg.changed
        else D.settings["text-secondary"].value
    )
    out.write(f"{reg.name:>18}")
    out.write(RESET_COLOR)
    out.write(" ")
    out.write(reg.hex_str)


def write_gp_decimal(out: Output, reg: GeneralPurposeRegister):
    out.write(f"{reg.value_int:>{len(reg.hex_str)+19}}")


def write_rflags(out: Output, flags: RflagsRegister):
    highlight = D.settings["text-highlight"].value
    secondary = D.settings["text-secondary"].value
    open_bracket = f"{secondary}{{{RESET_COLOR}"
    close_bracket = f"{secondary}}}{RESET_COLOR}"
    out.write(highlight if flags.changed else secondary)
    out.write(flags.name)
    out.write(RESET_COLOR)
    out.write(f" {open_bracket} ")
    write_flag(out, "DF", flags.df, flags.df_changed)
    out.write(f" {close_bracket} {open_bracket} ")
    write_flag(out, "TF", flags.tf, flags.tf_changed)
    out.write(" ")
    write_flag(out, "IF", flags.if_, flags.if_changed)
    out.write(" ")
    write_flag(out, "IOPL", flags.iopl, flags.iopl_changed)
    out.write(" ")
    write_flag(out, "NT", flags.nt, flags.nt_changed)
    out.write(" ")
    write_flag(out, "RF", flags.rf, flags.rf_changed)
    out.write(" ")
    write_flag(out, "VM", flags.vm, flags.vm_changed)
    out.write(" ")
    write_flag(out, "AC", flags.ac, flags.ac_changed)
    out.write(" ")
    write_flag(out, "VIF", flags.vif, flags.vif_changed)
    out.write(" ")
    write_flag(out, "VIP", flags.vip, flags.vip_changed)
    out.write(" ")
    write_flag(out, "ID", flags.id, flags.id_changed)
    out.write(f" {close_bracket} {open_bracket} ")
    write_flag(out, "CF", flags.cf, flags.cf_changed)
    out.write(" ")
    write_flag(out, "PF", flags.pf, flags.pf_changed)
    out.write(" ")
    write_flag(out, "AF", flags.af, flags.af_changed)
    out.write(" ")
    write_flag(out, "ZF", flags.zf, flags.zf_changed)
    out.write(" ")
    write_flag(out, "SF", flags.sf, flags.sf_changed)
    out.write(" ")
    write_flag(out, "OF", flags.of, flags.of_changed)
    out.write(f" {close_bracket}\n")


def write_mxcsr(out: Output, flags: MxcsrRegister):
    highlight = D.settings["text-highlight"].value
    secondary = D.settings["text-secondary"].value
    open_bracket = f"{secondary}{{{RESET_COLOR}"
    close_bracket = f"{secondary}}}{RESET_COLOR}"
    out.write(highlight if flags.changed else secondary)
    out.write(flags.name)
    out.write(RESET_COLOR)
    out.write(f" {open_bracket} ")
    write_flag(out, "FTZ", flags.ftz, flags.ftz_changed)
    out.write(" ")
    write_flag(out, "RC", flags.rc, flags.rc_changed)
    out.write(f" {close_bracket} {open_bracket} ")
    write_flag(out, "PM", flags.pm, flags.pm_changed)
    out.write(" ")
    write_flag(out, "UM", flags.um, flags.um_changed)
    out.write(" ")
    write_flag(out, "OM", flags.om, flags.om_changed)
    out.write(" ")
    write_flag(out, "ZM", flags.zm, flags.zm_changed)
    out.write(" ")
    write_flag(out, "DM", flags.dm, flags.dm_changed)
    out.write(" ")
    write_flag(out, "IM", flags.im, flags.im_changed)
    out.write(f" {close_bracket} {open_bracket} ")
    write_flag(out, "DAZ", flags.daz, flags.daz_changed)
    out.write(f" {close_bracket} {open_bracket} ")
    write_flag(out, "PE", flags.pe, flags.pe_changed)
    out.write(" ")
    write_flag(out, "UE", flags.ue, flags.ue_changed)
    out.write(" ")
    write_flag(out, "OE", flags.oe, flags.oe_changed)
    out.write(" ")
    write_flag(out, "ZE", flags.ze, flags.ze_changed)
    out.write(" ")
    write_flag(out, "DE", flags.de, flags.de_changed)
    out.write(" ")
    write_flag(out, "IE", flags.ie, flags.ie_changed)
    out.write(f" {close_bracket}\n")


def write_flag(out: Output, name: str, value: int, changed: bool):
    if changed:
        out.write(FONT_UNDERLINE)
    if not value:
        out.write(D.settings["text-secondary"].value)
    out.write(name)
    out.write(RESET_COLOR)


def write_avx(out: Output, regs: list[AvxRegister]):
    highlight = D.settings["text-highlight"].value
    secondary = D.settings["text-secondary"].value

    out.write(f"     {secondary}")
    for i in reversed(range(16, 32)):
        out.write(f" {i:>3}")
    out.write("      ")
    for i in reversed(range(16)):
        out.write(f" {i:>3}")
    out.write(f"{RESET_COLOR}\n")

    for reg in regs:
        out.write(highlight if reg.changed_ymm else secondary)
        out.write(f"{reg.name_ymm:>5}")
        out.write(RESET_COLOR)
        for i in reversed(range(16, 32)):
            out.write(f" {reg.values[i]:>3}")
        out.write(highlight if reg.changed_xmm else secondary)
        out.write(f" {reg.name_xmm:>5}")
        out.write(RESET_COLOR)
        for i in reversed(range(16)):
            out.write(f" {reg.values[i]:>3}")
        out.write("\n")


def write_segment(out: Output, regs: list[SegmentRegister]):
    highlight = D.settings["text-highlight"].value
    secondary = D.settings["text-secondary"].value
    for i, reg in enumerate(regs):
        if i:
            out.write("  ")
        out.write(highlight if reg.changed else secondary)
        out.write(reg.name)
        out.write(RESET_COLOR)
        out.write(f" {reg.hex_str}")
    out.write("\n")
