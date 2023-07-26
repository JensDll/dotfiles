import collections
from abc import abstractmethod
from functools import cached_property
from itertools import islice
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]

from .commands import BoolOption, Command, Configurable, Outputable, Togglable
from .utils import RESET_COLOR, fetch_gdb, fetch_instructions

if TYPE_CHECKING:
    from gdb import RegisterDescriptor  # pyright: ignore [reportMissingModuleSource]

    from . import DashboardOptions
    from .modules import AlignmentOptions, AssemblyOptions, RegistryOptions
    from .utils import WriteWrapper


class Module(Command, Togglable, Configurable, Outputable):
    def __init__(
        self,
        /,
        dashboard_options,  # type: DashboardOptions
        **kwargs,
    ):
        self.o = dashboard_options
        self.name = self.__class__.__name__

        super().__init__(
            command_name=f"dashboard {self.name.lower()}",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
            command_doc=self.__doc__,
            **kwargs,
        )

    @abstractmethod
    def render(self, width, height, write):
        pass

    def divider(self, width, height, write):
        if not self.o["show-divider"].value:
            write("\n")
            return

        before = self.o["divider-fill-char"].value * (width // 16)
        name = f" {self.name} "
        after = self.o["divider-fill-char"].value * (width - len(before) - len(name))

        write(self.o["text-divider"].value)
        write(before)
        write(self.o["text-divider-title"].value)
        write(name)
        write(self.o["text-divider"].value)
        write(after)
        write(RESET_COLOR)
        write("\n")


class Alignment(Module):
    """Print 64-byte-block formatted memory to see if instructions cross block boundaries"""

    ORDER = 0
    BLOCK_SIZE = 64

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        _, _, _, pc = fetch_gdb()

        residue_class = pc & (self.BLOCK_SIZE - 1)
        self.start = pc - residue_class
        self.end = self.start + self.BLOCK_SIZE

    def render(self, width, height, write):
        if width < 115:
            per_row = 16
        else:
            per_row = 32

        padding = per_row * 2

        inferior, _, architecture, pc = fetch_gdb()

        instruction_length = fetch_instructions(architecture, pc)[0]["length"]

        memory = inferior.read_memory(
            self.start - padding, self.BLOCK_SIZE + padding * 2
        )

        instruction_start = padding + (pc & (self.BLOCK_SIZE - 1))
        instruction_end = instruction_start + instruction_length

        color = None

        for i, byte in enumerate(memory):
            if i == padding:
                write("\n")
            elif i == padding + self.BLOCK_SIZE:
                write("\n")

            if i == instruction_start:
                write(self.o["text-highlight"].value)
                color = self.o["text-highlight"].value
            elif i == instruction_end:
                write(RESET_COLOR)
                color = None

            if i & (per_row - 1) == 0:
                write(RESET_COLOR)
                write(self.o["text-secondary"].value)
                write(f"{pc + i - instruction_start:#016x} ")
                write(RESET_COLOR)
                if color:
                    write(color)

            write(f" {byte.hex()}")  # type: ignore

            if (i + 1) & (per_row - 1) == 0:
                write("\n")

        if pc + instruction_length >= self.end:
            self.start += self.BLOCK_SIZE
            self.end += self.BLOCK_SIZE

    @cached_property
    def options(self):  # type:  () -> AlignmentOptions
        return {}


class Assembly(Module):
    """Print assembly information"""

    ORDER = 1

    def render(self, width, height, write):
        inferior, frame, architecture, pc = fetch_gdb()

        instructions = fetch_instructions(architecture, pc, 6)

        max_instruction_width = (
            max(instruction["length"] for instruction in instructions) * 2
        )
        max_instruction_width += (
            (max_instruction_width // 2) + (max_instruction_width % 2) - 1
        )

        try:
            flavor = str(gdb.parameter("disassembly-flavor"))
        except:
            flavor = "att"

        function = frame.function()

        function_address = int(
            function.value().address.cast(gdb.lookup_type("unsigned long"))
        )

        max_offset_width = len(str(instructions[-1]["addr"] - function_address))

        self.write_line(
            instruction=instructions[0],
            max_instruction_width=max_instruction_width,
            flavor=flavor,
            opcode_color=self.o["text-highlight"].value,
            inferior=inferior,
            write=write,
            function=function,
            function_address=function_address,
            max_offset_width=max_offset_width,
        )

        for instruction in islice(instructions, 1, None):
            self.write_line(
                instruction=instruction,
                max_instruction_width=max_instruction_width,
                flavor=flavor,
                opcode_color=RESET_COLOR,
                inferior=inferior,
                write=write,
                function=function,
                function_address=function_address,
                max_offset_width=max_offset_width,
            )

    def write_line(
        self,
        *,
        instruction,
        max_instruction_width,
        flavor,
        opcode_color,
        inferior,
        write,
        function=None,
        function_address=-1,
        max_offset_width=-1,
    ):
        address = instruction["addr"]
        length = instruction["length"]
        assembly = syntax_highlight(instruction["asm"], flavor)
        opcode = inferior.read_memory(address, length)

        if function is None:
            write(
                f"{self.o['text-secondary']}{address:#016x}{RESET_COLOR}  "
                f"{opcode_color}{opcode.hex(' ', 1):<{max_instruction_width}}{RESET_COLOR}  "
                f"{assembly}"
            )
            return

        offset = address - function_address

        write(
            f"{self.o['text-secondary']}{address:#016x}{RESET_COLOR}  "
            f"{opcode_color}{opcode.hex(' ', 1):<{max_instruction_width}}{RESET_COLOR}  "
            f"{self.o['text-secondary']}{function}+{offset:<{max_offset_width}}{RESET_COLOR}  "
            f"{assembly}"
        )

    @cached_property
    def options(self):  # type:  () -> AssemblyOptions
        return {
            "show-function": BoolOption("Show current function and offset", value="on"),
        }


class Registers(Module):
    """Print register information"""

    ORDER = 2

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        _, _, architecture, _ = fetch_gdb()

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
        self.render_general(width // 22, frame, write)
        write("\n")
        self.render_segment(width // 16, frame, write)
        write("\n")
        self.render_eflags(width, frame, write)

    def render_general(
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

    def render_segment(
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

    def render_eflags(
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

        write("  ")

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

        write("  ")

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
    def options(self):  # type:  () -> RegistryOptions
        return {}


def syntax_highlight(source, hint):
    try:
        import pygments  # pyright: ignore [reportMissingModuleSource]
        import pygments.formatters  # pyright: ignore [reportMissingModuleSource]
        import pygments.lexers  # pyright: ignore [reportMissingModuleSource]

        if hint == "intel":
            lexer = pygments.lexers.NasmLexer()
        elif hint == "att":
            lexer = pygments.lexers.GasLexer()
        else:
            lexer = pygments.lexers.get_lexer_for_filename(hint)

        formatter = pygments.formatters.TerminalFormatter()

        return pygments.highlight(source, lexer, formatter)
    except ImportError:
        return source
