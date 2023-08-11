from functools import cached_property
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.commands import BoolOption
from gdbdash.utils import RESET_COLOR

from .module import Module

if TYPE_CHECKING:
    from gdb import (  # pyright: ignore [reportMissingModuleSource]
        RegisterDescriptor,
        Type,
    )
    from gdbdash.dashboard import DashboardOptions
    from gdbdash.utils import WriteWrapper

    from .registers import RegisterOptions


class Registers(Module):
    """Print register information"""

    ORDER = 300

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        frame = gdb.selected_frame()
        architecture = frame.architecture()

        int_type = architecture.integer_type(64, False)

        self.general_purpose = []  # type: list[GeneralPurposeRegister]
        self.segment = []  # type: list[SegmentRegister]

        for descriptor in architecture.registers("general"):
            if descriptor.name == "eflags":
                self.eflags = EFlagsRegister(descriptor, int_type, self.o)
            elif descriptor.name == "rip":
                continue
            elif descriptor.name.endswith("s"):
                self.segment.append(SegmentRegister(descriptor, int_type, self.o))
            else:
                self.general_purpose.append(
                    GeneralPurposeRegister(descriptor, int_type, self.o)
                )

    def render(self, width, height, write):
        frame = gdb.selected_frame()
        self.write_general_purpose(width // 25, frame, write)
        self.write_eflags(frame, write)
        self.write_segment(frame, write)

    def write_general_purpose(
        self, per_row, frame, write
    ):  # type: (int, gdb.Frame, WriteWrapper) -> None
        registers_left = len(self.general_purpose)
        stop = min(registers_left, per_row)
        row = 0

        new_line_after_row = (
            self.options["show-32"].value or self.options["show-decimal"].value
        )

        while stop > 0:
            for col in range(0, stop):
                register = self.general_purpose[row * per_row + col]
                write(register.get_value_64(frame))

            write("\n")

            if self.options["show-32"].value:
                for col in range(0, stop):
                    register = self.general_purpose[row * per_row + col]
                    write(register.get_value_32())
                write("\n")

            if self.options["show-decimal"].value:
                for col in range(0, stop):
                    register = self.general_purpose[row * per_row + col]
                    write(register.get_value_decimal())
                write("\n")

            registers_left -= per_row
            stop = min(registers_left, per_row)
            row += 1

            if new_line_after_row:
                write("\n")

        if not new_line_after_row:
            write("\n")

    def write_eflags(self, frame, write):  # type: (gdb.Frame, WriteWrapper) -> None
        write(self.eflags.get_value(frame))
        write("\n")

    def write_segment(self, frame, write):  # type: (gdb.Frame, WriteWrapper) -> None
        for register in self.segment:
            write(register.get_value(frame))
        write("\n")

    @cached_property
    def options(self):  # type: () -> RegisterOptions
        return {
            "show-32": BoolOption(
                "Show 32-bit version of general purpose register", True
            ),
            "show-decimal": BoolOption(
                "Show decimal value of general purpose register", True
            ),
        }


class Register:
    def __init__(
        self,
        descriptor,  # type: RegisterDescriptor
        int_type,  # type: Type
        options,  # type: DashboardOptions
    ):
        self.descriptor = descriptor
        self.name = descriptor.name
        self.int_type = int_type
        self.options = options


class GeneralPurposeRegister(Register):
    MAP32 = {
        "rax": "eax",
        "rbx": "ebx",
        "rcx": "ecx",
        "rdx": "edx",
        "rsi": "esi",
        "rdi": "edi",
        "rbp": "ebp",
        "rsp": "esp",
        "r8": "r8d",
        "r9": "r9d",
        "r10": "r10d",
        "r11": "r11d",
        "r12": "r12d",
        "r13": "r13d",
        "r14": "r14d",
        "r15": "r15d",
    }

    MAP16 = {
        "eax": "ax",
        "ebx": "bx",
        "ecx": "cx",
        "edx": "dx",
        "esi": "si",
        "edi": "di",
        "ebp": "bp",
        "esp": "sp",
        "r8d": "r8w",
        "r9d": "r9w",
        "r10d": "r10w",
        "r11d": "r11w",
        "r12d": "r12w",
        "r13d": "r13w",
        "r14d": "r14w",
        "r15d": "r15w",
    }

    MAP8H = {
        "ax": "ah",
        "bx": "bh",
        "cx": "ch",
        "dx": "dh",
    }

    MAP8L = {
        "ax": "al",
        "bx": "bl",
        "cx": "cl",
        "dx": "dl",
        "si": "sil",
        "di": "dil",
        "bp": "bpl",
        "sp": "spl",
        "r8w": "r8b",
        "r9w": "r9b",
        "r10w": "r10b",
        "r11w": "r11b",
        "r12w": "r12b",
        "r13w": "r13b",
        "r14w": "r14b",
        "r15w": "r15b",
    }

    def __init__(
        self,
        descriptor,  # type: RegisterDescriptor
        int_type,  # type: Type
        options,  # type: DashboardOptions
    ):
        super().__init__(descriptor, int_type, options)

        self.name32 = self.MAP32[descriptor.name]

        self.value64 = None  # type: int | None

    def get_value_64(self, frame):  # type: (gdb.Frame) -> str
        self.value = frame.read_register(self.descriptor)
        int_value = self.value.cast(self.int_type)

        value64 = int(int_value)

        if self.value64 is not None and self.value64 != value64:
            self.color = self.options["text-highlight"]
        else:
            self.color = self.options["text-secondary"]

        self.value64 = value64
        self.value32 = int(int_value & 0xFFFF_FFFF)

        return f"{self.color}{self.name:<4}{RESET_COLOR} {value64:#018x}  "

    def get_value_32(self):  # type: () -> str
        return (
            f"{self.color}{self.name32:<4}{RESET_COLOR}           {self.value32:08x}  "
        )

    def get_value_decimal(self):  # type: () -> str
        return f" {self.value.format_string(format='d'):<24}"


class SegmentRegister(Register):
    def __init__(
        self,
        descriptor,  # type: RegisterDescriptor
        int_type,  # type: Type
        options,  # type: DashboardOptions
    ):
        super().__init__(descriptor, int_type, options)

        self.value = None  # type: int | None

    def get_value(self, frame):  # type: (gdb.Frame) -> str
        value = int(frame.read_register(self.descriptor))

        if self.value is not None and self.value != value:
            color = self.options["text-highlight"]
        else:
            color = self.options["text-secondary"]

        self.value = value

        return f"{color}{self.name:>2}{RESET_COLOR} {value:#06x}  "


class EFlagsRegister(Register):
    def __init__(
        self,
        descriptor,  # type: RegisterDescriptor
        int_type,  # type: Type
        options,  # type: DashboardOptions
    ):
        super().__init__(descriptor, int_type, options)

    def get_value(self, frame):  # type: (gdb.Frame) -> str
        value = int(frame.read_register(self.descriptor))

        # Control flags
        df = (value >> 10) & 1  # Direction flag

        # System flags
        tf = (value >> 8) & 1  # Trap flag
        _if = (value >> 9) & 1  # Interrupt enable flag
        iopl = (value >> 12) & 3  # I/O privilege level
        nt = (value >> 14) & 1  # Nested task flag
        rf = (value >> 16) & 1  # Resume flag
        vm = (value >> 17) & 1  # Virtual 8086 mode flag
        ac = (value >> 18) & 1  # Alignment check / Access control flag
        vif = (value >> 19) & 1  # Virtual interrupt flag
        vip = (value >> 20) & 1  # Virtual interrupt pending flag
        id = (value >> 21) & 1  # ID flag

        # Status flags
        cf = value & 1  # Carry flag
        pf = (value >> 2) & 1  # Parity flag
        af = (value >> 4) & 1  # Auxiliary carry flag
        zf = (value >> 6) & 1  # Zero flag
        sf = (value >> 7) & 1  # Sign flag
        of = (value >> 11) & 1  # Overflow flag

        return (
            f"{self.flag('DF', df)}   "
            f"{self.flag('TF', tf)} {self.flag('IF', _if)} {self.flag('IOPL', iopl)} {self.flag('NT', nt)} {self.flag('RF', rf)} "
            f"{self.flag('VM', vm)} {self.flag('AC', ac)} {self.flag('VIF', vif)} {self.flag('VIP', vip)} {self.flag('ID', id)}   "
            f"{self.flag('CF', cf)} {self.flag('PF', pf)} {self.flag('AF', af)} {self.flag('ZF', zf)} {self.flag('SF', sf)} {self.flag('OF', of)}\n"
        )

    def flag(self, name, value):
        if value:
            return f"{self.options['text-highlight']}{name}{RESET_COLOR}"
        else:
            return f"{self.options['text-secondary']}{name}{RESET_COLOR}"
