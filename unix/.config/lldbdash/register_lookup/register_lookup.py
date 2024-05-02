import dataclasses
import typing

import lldb
from lldbdash.common import not_none

from .register import (
    AvxRegister,
    GeneralPurposeRegister,
    MxcsrRegister,
    RflagsRegister,
    SegmentRegister,
)
from .register_set import get_avx_reg_set, get_fp_reg_set, get_gp_reg_set

Entries = dict[str, "RegisterLookup.Entry"]


class RegisterLookup:
    _instance: typing.Optional["RegisterLookup"] = None

    @dataclasses.dataclass
    class Entry:
        indices: list[int]
        prev_values: list[int]

    def __init__(self, frame: lldb.SBFrame):
        entries = Entries()
        init_gp(entries, frame)
        init_fp(entries, frame)
        init_avx(entries, frame)
        self.entries = entries

    @classmethod
    def new_or_cached(cls, frame: lldb.SBFrame) -> "RegisterLookup":
        if not cls._instance:
            cls._instance = cls(frame)
        return cls._instance

    def read_gp(self, reg_set: lldb.SBValue, name: str):
        entry = self.entries[name]
        values: list[lldb.SBValue] = [reg_set.GetChildAtIndex(i) for i in entry.indices]
        register = GeneralPurposeRegister(values, entry.prev_values[0])
        entry.prev_values[0] = register.value_uint
        return register

    def read_segment(self, reg_set: lldb.SBValue, name: str):
        entry = self.entries[name]
        value: lldb.SBValue = reg_set.GetChildAtIndex(entry.indices[0])
        register = SegmentRegister(value, entry.prev_values[0])
        entry.prev_values[0] = register.value_uint
        return register

    def read_rflags(self, reg_set: lldb.SBValue):
        entry = self.entries["rflags"]
        value: lldb.SBValue = reg_set.GetChildAtIndex(entry.indices[0])
        register = RflagsRegister(value, entry.prev_values[0])
        entry.prev_values[0] = register.value_uint
        return register

    def read_mxcsr(self, reg_set: lldb.SBValue):
        entry = self.entries["mxcsr"]
        value: lldb.SBValue = reg_set.GetChildAtIndex(entry.indices[0])
        register = MxcsrRegister(value, entry.prev_values[0])
        entry.prev_values[0] = register.value_uint
        return register

    def read_avx(self, avx_reg_set: lldb.SBValue, fp_reg_set: lldb.SBValue, name: str):
        entry = self.entries[name]
        ymm: lldb.SBValue = avx_reg_set.GetChildAtIndex(entry.indices[0])
        xmm: lldb.SBValue = fp_reg_set.GetChildAtIndex(entry.indices[1])
        register = AvxRegister(ymm, xmm, entry.prev_values)
        entry.prev_values = register.values
        return register


def init_gp(entries: Entries, frame: lldb.SBFrame):
    gp_reg_set = get_gp_reg_set(frame)
    gp_index = dict[str, int]((t[1].GetName(), t[0]) for t in enumerate(gp_reg_set))

    for regs in (
        ["rax", "eax", "ax", "al"],
        ["rbx", "ebx", "bx", "bl"],
        ["rcx", "ecx", "cx", "cl"],
        ["rdx", "edx", "dx", "dl"],
        ["rsi", "esi", "si", "sil"],
        ["rdi", "edi", "di", "dil"],
        ["rbp", "ebp", "bp", "bpl"],
        ["rsp", "esp", "sp", "spl"],
        ["r8", "r8d", "r8w", "r8l"],
        ["r9", "r9d", "r9w", "r9l"],
        ["r10", "r10d", "r10w", "r10l"],
        ["r11", "r11d", "r11w", "r11l"],
        ["r12", "r12d", "r12w", "r12l"],
        ["r13", "r13d", "r13w", "r13l"],
        ["r14", "r14d", "r14w", "r14l"],
        ["r15", "r15d", "r15w", "r15l"],
    ):
        indices = list[int](filter(not_none, (gp_index.get(r, None) for r in regs)))
        entries[regs[0]] = RegisterLookup.Entry(
            indices, [gp_reg_set.GetChildAtIndex(indices[0]).GetValueAsUnsigned()]
        )

    for reg in ["cs", "ds", "ss", "es", "fs", "gs", "rflags"]:
        index = gp_index.get(reg, None)
        if index is None:
            continue
        entries[reg] = RegisterLookup.Entry(
            [index], [gp_reg_set.GetChildAtIndex(index).GetValueAsUnsigned()]
        )


def init_avx(entries: Entries, frame: lldb.SBFrame):
    avx_reg_set = get_avx_reg_set(frame)
    avx_index = dict[str, int]((t[1].GetName(), t[0]) for t in enumerate(avx_reg_set))

    for i in range(16):
        ymm = f"ymm{i}"
        xmm = f"xmm{i}"
        index = avx_index.get(ymm, None)
        if index is None:
            continue
        xmm_entry = entries[xmm]
        entries[ymm] = RegisterLookup.Entry(
            [index, xmm_entry.indices[0]],
            [
                child.GetValueAsUnsigned()
                for child in avx_reg_set.GetChildAtIndex(index)
            ],
        )


def init_fp(entries: Entries, frame: lldb.SBFrame):
    fp_reg_set = get_fp_reg_set(frame)
    fp_index = dict[str, int]((t[1].GetName(), t[0]) for t in enumerate(fp_reg_set))

    for i in range(16):
        xmm = f"xmm{i}"
        index = fp_index.get(xmm, None)
        if index is None:
            continue
        entries[xmm] = RegisterLookup.Entry(
            [index],
            [child.GetValueAsUnsigned() for child in fp_reg_set.GetChildAtIndex(index)],
        )

    for reg in ["mxcsr"]:
        index = fp_index.get(reg, None)
        if index is None:
            continue
        entries[reg] = RegisterLookup.Entry(
            [index], [fp_reg_set.GetChildAtIndex(index).GetValueAsUnsigned()]
        )
