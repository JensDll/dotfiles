from functools import cached_property
from typing import TYPE_CHECKING

import gdb
from gdbdash.commands import BoolOption

from .module import Module
from .registers_display import (
    EflagsRegister,
    GeneralPurposeRegister,
    MxcsrRegister,
    SegmentRegister,
    VectorRegister,
)

if TYPE_CHECKING:
    from gdbdash.utils import WriteWrapper

    from .registers import RegisterOptions


class Registers(Module):
    """Print register information"""

    ORDER = 3

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        self.general_purpose_registers = []  # type: list[GeneralPurposeRegister]
        self.segment_registers = []  # type: list[SegmentRegister]
        self.vector_registers = []  # type: list[VectorRegister]

        for descriptor in self.architecture.registers("general"):
            if descriptor.name == "eflags":
                self.eflags_register = EflagsRegister(descriptor, self.uint64_t, self.o)
            elif descriptor.name == "rip":
                continue
            elif descriptor.name.endswith("s"):
                self.segment_registers.append(
                    SegmentRegister(descriptor, self.uint64_t, self.o)
                )
            else:
                self.general_purpose_registers.append(
                    GeneralPurposeRegister(descriptor, self.uint64_t, self.o)
                )

        for descriptor in self.architecture.registers("vector"):
            if descriptor.name == "mxcsr":
                self.mxcsr_register = MxcsrRegister(descriptor, self.uint64_t, self.o)
            elif descriptor.name.startswith("ymm"):
                self.vector_registers.append(
                    VectorRegister(descriptor, self.uint64_t, self.o)
                )

    def render(self, width, height, write):
        frame = gdb.selected_frame()

        self.write_general_purpose_registers(width // 25, frame, write)

        if self.options["show-segment"].value:
            write("\n")
            self.write_segment_registers(frame, write)

        if self.options["show-eflags"].value:
            write("\n")
            self.write_eflags_register(frame, write)

        if self.options["show-mxcsr"].value:
            write("\n")
            self.write_mxcsr_register(frame, write)

        if self.options["show-vector"].value:
            write("\n")
            self.write_vector_registers(frame, write)

        write("\n")

    def write_general_purpose_registers(
        self, per_row, frame, write
    ):  # type: (int, gdb.Frame, WriteWrapper) -> None
        def write_row():
            for col in range(0, stop):
                register = self.general_purpose_registers[row * per_row + col]
                write(register.get_value(frame))

            if self.options["show-32"].value:
                write("\n")
                for col in range(0, stop):
                    register = self.general_purpose_registers[row * per_row + col]
                    write(register.get_value_32())

            if self.options["show-decimal"].value:
                write("\n")
                for col in range(0, stop):
                    register = self.general_purpose_registers[row * per_row + col]
                    write(register.get_value_decimal())

        registers_left = len(self.general_purpose_registers)
        stop = min(registers_left, per_row)
        row = 0
        write_row()
        registers_left -= per_row
        stop = min(registers_left, per_row)
        row = 1

        while stop > 0:
            write("\n")
            write_row()
            registers_left -= per_row
            stop = min(registers_left, per_row)
            row += 1

    def write_segment_registers(
        self, frame, write
    ):  # type: (gdb.Frame, WriteWrapper) -> None
        for register in self.segment_registers:
            write(register.get_value(frame))

    def write_eflags_register(
        self, frame, write
    ):  # type: (gdb.Frame, WriteWrapper) -> None
        write(self.eflags_register.get_value(frame))

    def write_mxcsr_register(
        self, frame, write
    ):  # type: (gdb.Frame, WriteWrapper) -> None
        write(self.mxcsr_register.get_value(frame))

    def write_vector_registers(
        self, frame, write
    ):  # type: (gdb.Frame, WriteWrapper) -> None
        for register in self.vector_registers[:-1]:
            write(register.get_value(frame))
            write("\n")
        write(self.vector_registers[-1].get_value(frame))

    @cached_property
    def options(self):  # type: () -> RegisterOptions
        return {
            "show-32": BoolOption(
                "Visibility of general purpose registers 32-bit version", True
            ),
            "show-decimal": BoolOption(
                "Visibility of general purpose registers decimal value", True
            ),
            "show-segment": BoolOption("Visibility of segment registers", False),
            "show-eflags": BoolOption("Visibility of eflags register", True),
            "show-mxcsr": BoolOption("Visibility of mxcsr register", False),
            "show-vector": BoolOption("Visibility of vector registers", False),
        }
