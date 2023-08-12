from functools import cached_property
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.commands import BoolOption

from .module import Module
from .register_wrapper import EFlags, GeneralPurpose, Segment

if TYPE_CHECKING:
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

        self.general_purpose = []  # type: list[GeneralPurpose]
        self.segment = []  # type: list[Segment]

        for descriptor in architecture.registers("general"):
            if descriptor.name == "eflags":
                self.eflags = EFlags(descriptor, int_type, self.o)
            elif descriptor.name == "rip":
                continue
            elif descriptor.name.endswith("s"):
                self.segment.append(Segment(descriptor, int_type, self.o))
            else:
                self.general_purpose.append(
                    GeneralPurpose(descriptor, int_type, self.o)
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
                write(register.get_value(frame))
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

            if new_line_after_row:
                write("\n")

            registers_left -= per_row
            stop = min(registers_left, per_row)
            row += 1

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
                "Show 32-bit version of general purpose registers", True
            ),
            "show-decimal": BoolOption(
                "Show decimal value of general purpose registers", True
            ),
        }
