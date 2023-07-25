from abc import abstractmethod
from functools import cached_property
from itertools import islice
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]

from .commands import BoolOption, Command, Configurable, Outputable, Togglable
from .utils import RESET_COLOR, fetch_gdb, fetch_instructions

if TYPE_CHECKING:
    from . import DashboardOptions
    from .modules import AlignmentOptions, AssemblyOptions, RegistryOptions


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
                write(self.o["text-200"].value)
                write(f"{pc + i - instruction_start:#016x}  ")
                write(self.o["text-100"].value)
                if color:
                    write(color)

            write(byte.hex() + " ")  # type: ignore

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

        if not self.options["show-function"].value:
            self.write_line(
                instruction=instructions[0],
                max_instruction_width=max_instruction_width,
                flavor=flavor,
                opcode_color=self.o["text-highlight"].value,
                inferior=inferior,
                write=write,
            )

            for instruction in islice(instructions, 1, None):
                self.write_line(
                    instruction=instruction,
                    max_instruction_width=max_instruction_width,
                    flavor=flavor,
                    opcode_color=self.o["text-100"].value,
                    inferior=inferior,
                    write=write,
                )

            return

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
                opcode_color=self.o["text-100"].value,
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
                f"{self.o['text-200'].value}{address:#016x}  {opcode_color}{opcode.hex(' ', 1):<{max_instruction_width}}  {RESET_COLOR}{assembly}"
            )
            return

        offset = address - function_address

        write(
            f"{self.o['text-200'].value}{address:#016x}  {opcode_color}{opcode.hex(' ', 1):<{max_instruction_width}}  {RESET_COLOR}{self.o['text-200'].value}{function}+{offset:<{max_offset_width}}  {RESET_COLOR}{assembly}"
        )

    @cached_property
    def options(self):  # type:  () -> AssemblyOptions
        return {
            "show-function": BoolOption("Show current function and offset", value="on"),
        }


class Registers(Module):
    """Print register information"""

    ORDER = 2

    def render(self, width, height, write):
        pass

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
