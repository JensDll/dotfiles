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


@dataclasses.dataclass
class Entry:
    indices: list[int]
    values: list[int]
    prev_values: list[int] = dataclasses.field(init=False)
    pc: int
    pc_change_count = -1

    def __post_init__(self):
        self.prev_values = self.values.copy()


Entries = dict[str, Entry]


class RegisterReader:
    _frame: lldb.SBFrame
    _instance: typing.Optional["RegisterReader"] = None

    def __init__(self, frame: lldb.SBFrame):
        self.entries = Entries()

        self.update_reg_sets(frame)
        pc = frame.GetPC()

        gp_index = dict[str, int](
            (t[1].GetName(), t[0]) for t in enumerate(self.gp_reg_set)
        )
        fp_index = dict[str, int](
            (t[1].GetName(), t[0]) for t in enumerate(self.fp_reg_set)
        )
        avx_index = dict[str, int](
            (t[1].GetName(), t[0]) for t in enumerate(self.avx_reg_set)
        )

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
            idx_64 = gp_index.get(regs[0])
            idx_32 = gp_index.get(regs[1])
            idx_16 = gp_index.get(regs[2])
            idx_8 = gp_index.get(regs[3])

            if idx_64 is not None:
                self.entries[regs[0]] = Entry(
                    [
                        idx_64,
                        typing.cast(int, idx_32),
                        typing.cast(int, idx_16),
                        typing.cast(int, idx_8),
                    ],
                    [self.gp_reg_set.GetChildAtIndex(idx_64).GetValueAsUnsigned()],
                    pc,
                )

            if idx_32 is not None:
                self.entries[regs[1]] = Entry(
                    [idx_32, typing.cast(int, idx_16), typing.cast(int, idx_8)],
                    [self.gp_reg_set.GetChildAtIndex(idx_32).GetValueAsUnsigned()],
                    pc,
                )

            if idx_16 is not None:
                self.entries[regs[2]] = Entry(
                    [idx_16, typing.cast(int, idx_8)],
                    [self.gp_reg_set.GetChildAtIndex(idx_16).GetValueAsUnsigned()],
                    pc,
                )

            if idx_8 is not None:
                self.entries[regs[3]] = Entry(
                    [idx_8],
                    [self.gp_reg_set.GetChildAtIndex(idx_8).GetValueAsUnsigned()],
                    pc,
                )

        for reg in ["cs", "ds", "ss", "es", "fs", "gs", "rflags"]:
            index = gp_index.get(reg)
            if index is None:
                continue
            values = [self.gp_reg_set.GetChildAtIndex(index).GetValueAsUnsigned()]
            self.entries[reg] = Entry([index], values, pc)

        for i in range(16):
            xmm = f"xmm{i}"
            index = fp_index.get(xmm)
            if index is None:
                continue
            values = [
                child.GetValueAsUnsigned()
                for child in self.fp_reg_set.GetChildAtIndex(index)
            ]
            self.entries[xmm] = Entry([index], values, pc)

        for reg in ["mxcsr"]:
            index = fp_index.get(reg)
            if index is None:
                continue
            values = [self.fp_reg_set.GetChildAtIndex(index).GetValueAsUnsigned()]
            self.entries[reg] = Entry([index], values, pc)

        for i in range(16):
            ymm = f"ymm{i}"
            xmm = f"xmm{i}"
            index = avx_index.get(ymm)
            if index is None:
                continue
            values = [
                child.GetValueAsUnsigned()
                for child in self.avx_reg_set.GetChildAtIndex(index)
            ]
            self.entries[ymm] = Entry([index, fp_index[xmm]], values, pc)

    @classmethod
    def new_or_cached(cls, frame: lldb.SBFrame) -> "RegisterReader":
        if cls._instance is None:
            cls._instance = cls(frame)
            cls._frame = frame
        if cls._frame != frame:
            cls._instance.update_reg_sets(frame)
        return cls._instance

    def update_reg_sets(self, frame: lldb.SBFrame):
        self.frame = frame
        for reg_set in frame.GetRegisters():
            name: str = reg_set.GetName().lower()
            if "general purpose" in name:
                self.gp_reg_set: lldb.SBValue = reg_set
            elif "advanced vector extensions" in name:
                self.avx_reg_set: lldb.SBValue = reg_set
            elif "floating point" in name:
                self.fp_reg_set: lldb.SBValue = reg_set

    def read_gp(self, name: str):
        entry, pc_changed = self.get_entry(name)
        values: list[lldb.SBValue] = [
            self.gp_reg_set.GetChildAtIndex(i) for i in entry.indices
        ]
        if pc_changed:
            entry.values[0] = values[0].GetValueAsUnsigned()
        return GeneralPurposeRegister(values, entry.prev_values[0])

    def read_segment(self, name: str):
        entry, pc_changed = self.get_entry(name)
        value: lldb.SBValue = self.gp_reg_set.GetChildAtIndex(entry.indices[0])
        if pc_changed:
            entry.values[0] = value.GetValueAsUnsigned()
        return SegmentRegister(value.GetName(), entry.values[0], entry.prev_values[0])

    def read_rflags(self):
        entry, pc_changed = self.get_entry("rflags")
        value: lldb.SBValue = self.gp_reg_set.GetChildAtIndex(entry.indices[0])
        if pc_changed:
            entry.values[0] = value.GetValueAsUnsigned()
        return RflagsRegister(value.GetName(), entry.values[0], entry.prev_values[0])

    def read_mxcsr(self):
        entry, pc_changed = self.get_entry("mxcsr")
        value: lldb.SBValue = self.fp_reg_set.GetChildAtIndex(entry.indices[0])
        if pc_changed:
            entry.values[0] = value.GetValueAsUnsigned()
        return MxcsrRegister(value.GetName(), entry.values[0], entry.prev_values[0])

    def read_avx(self, name: str):
        entry, pc_changed = self.get_entry(name)
        ymm: lldb.SBValue = self.avx_reg_set.GetChildAtIndex(entry.indices[0])
        xmm: lldb.SBValue = self.fp_reg_set.GetChildAtIndex(entry.indices[1])
        if pc_changed:
            entry.values = [child.GetValueAsUnsigned() for child in ymm]
        return AvxRegister(
            ymm.GetName(), xmm.GetName(), entry.values, entry.prev_values
        )

    def get_entry(self, name: str):
        entry = self.entries[name]
        pc = self.frame.GetPC()
        pc_changed = entry.pc != pc
        entry.pc = pc
        entry.pc_change_count += pc_changed
        if entry.pc_change_count == 1:
            entry.pc_change_count = 0
            entry.prev_values = entry.values.copy()
        return entry, pc_changed
