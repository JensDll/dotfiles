import dataclasses
import typing

import lldb
import lldbdash.common

from .register import Register
from .register_set import get_gp_register_set


class RegisterLookup:
    _instance: typing.Optional["RegisterLookup"] = None

    @dataclasses.dataclass
    class Entry:
        indices: list[int]
        prev_value: int

    def __init__(self, frame: lldb.SBFrame):
        gp_reg_set = get_gp_register_set(frame)

        gp_indices = dict[str, int](
            (t[1].GetName(), t[0]) for t in enumerate(gp_reg_set)
        )

        gp_regs = [
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
        ]

        entries = dict[str, RegisterLookup.Entry]()

        for regs in gp_regs:
            indices = list[int](
                filter(
                    lldbdash.common.not_none, (gp_indices.get(r, None) for r in regs)
                )
            )
            entries[regs[0]] = RegisterLookup.Entry(
                indices, gp_reg_set.GetChildAtIndex(indices[0]).GetValueAsUnsigned()
            )

        print(entries)

        self.entries = entries

    @classmethod
    def new_or_cached(cls, frame: lldb.SBFrame) -> "RegisterLookup":
        if not cls._instance:
            cls._instance = cls(frame)
        return cls._instance

    def read_register(self, reg_set: lldb.SBValue, name: str):
        entry = self.entries.get(name, None)
        if not entry:
            return
        register = Register(
            [reg_set.GetChildAtIndex(i) for i in entry.indices], entry.prev_value
        )
        entry.prev_value = register.int
        return register
