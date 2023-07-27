from functools import cached_property
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.utils import RESET_COLOR, fetch_instructions, fetch_pc

from .module import Module

if TYPE_CHECKING:
    from gdb import RegisterDescriptor  # pyright: ignore [reportMissingModuleSource]
    from gdbdash.utils import WriteWrapper

    from .registers import RegisterOptions


class Registers(Module):
    """Print register information"""

    ORDER = 300

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        frame = gdb.selected_frame()
        architecture = frame.architecture()

        self.segment = []  # type: list[RegisterDescriptor]
        self.general_purpose = []  # type: list[RegisterDescriptor]
        self.eflags = None  # type: RegisterDescriptor | None

        for descriptor in architecture.registers("general"):
            if descriptor.name == "eflags":
                self.eflags = descriptor
            elif descriptor.name.endswith("s"):
                self.segment.append(descriptor)
            else:
                self.general_purpose.append(descriptor)

    def render(self, width, height, write):
        frame = gdb.selected_frame()
        self.write_general_purpose_registers(width // 22, frame, write)
        self.write_eflags(width, frame, write)
        self.write_segment_registers(width // 16, frame, write)

    def write_general_purpose_registers(
        self, per_row, frame, write
    ):  # type: (int, gdb.Frame, WriteWrapper) -> None
        i = 0

        while True:
            for _ in range(0, per_row):
                if i >= len(self.general_purpose):
                    write("\n")
                    return

                register = self.general_purpose[i]
                value = int(frame.read_register(register))

                if value == getattr(self, register.name, value):
                    color = self.o["text-secondary"].value
                else:
                    color = self.o["text-highlight"].value

                write(f"{color}{register.name:>3}{RESET_COLOR} {value:#016x}  ")

                setattr(self, register.name, value)

                i += 1

            write("\n")

    def write_segment_registers(
        self, per_row, frame, write
    ):  # type: (int, gdb.Frame, WriteWrapper) -> None
        i = 0

        while True:
            for _ in range(0, per_row):
                if i >= len(self.segment):
                    write("\n")
                    return

                register = self.segment[i]
                value = int(frame.read_register(register))

                if value == getattr(self, register.name, value):
                    color = self.o["text-secondary"].value
                else:
                    color = self.o["text-highlight"].value

                write(f"{color}{register.name:>2}{RESET_COLOR} {value:#04x}  ")

                setattr(self, register.name, value)

                i += 1

            write("\n")

    def write_eflags(
        self, width, frame, write
    ):  # type: (int, gdb.Frame, WriteWrapper) -> None
        if self.eflags is None:
            return

        def write_flag(value, display):  # type: (int, str) -> None
            if value:
                write(f"{self.o['text-highlight']}{display}{RESET_COLOR} ")
            else:
                write(f"{self.o['text-secondary']}{display}{RESET_COLOR} ")

        value = int(frame.read_register(self.eflags))

        # Control flags
        df = (value >> 10) & 1  # Direction flag
        write_flag(df, "DF")
        self.df = df
        write("- ")
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
        write_flag(tf, "TF")
        write_flag(_if, "IF")
        write_flag(iopl, "IOPL")
        write_flag(nt, "NT")
        write_flag(rf, "RF")
        write_flag(vm, "VM")
        write_flag(ac, "AC")
        write_flag(vif, "VIF")
        write_flag(vip, "VIP")
        write_flag(id, "ID")
        self.tf = tf
        self._if = _if
        self.iopl = iopl
        self.nt = nt
        self.rf = rf
        self.vm = vm
        self.ac = ac
        self.vif = vif
        self.vip = vip
        self.id = id
        write("- ")
        # Status flags
        cf = value & 1  # Carry flag
        pf = (value >> 2) & 1  # Parity flag
        af = (value >> 4) & 1  # Auxiliary carry flag
        zf = (value >> 6) & 1  # Zero flag
        sf = (value >> 7) & 1  # Sign flag
        of = (value >> 11) & 1  # Overflow flag
        write_flag(cf, "CF")
        write_flag(pf, "PF")
        write_flag(af, "AF")
        write_flag(zf, "ZF")
        write_flag(sf, "SF")
        write_flag(of, "OF")
        self.cf = cf
        self.pf = pf
        self.af = af
        self.zf = zf
        self.sf = sf
        self.of = of

        write("\n")

    @cached_property
    def options(self):  # type: () -> RegisterOptions
        return {}
