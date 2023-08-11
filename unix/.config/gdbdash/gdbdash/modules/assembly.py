import re
from functools import cached_property
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.commands import IntOption
from gdbdash.utils import FONT_BOLD, RESET_COLOR, fetch_instructions, fetch_pc

from .module import Module

if TYPE_CHECKING:
    from gdbdash.utils import Instruction

    from .assembly import AssemblyOptions

try:
    import pygments  # pyright: ignore [reportMissingModuleSource]
    import pygments.formatters  # pyright: ignore [reportMissingModuleSource]
    import pygments.lexers  # pyright: ignore [reportMissingModuleSource]

    def syntax_highlight(source, hint):
        if hint == "intel":
            lexer = pygments.lexers.NasmLexer()
        elif hint == "att":
            lexer = pygments.lexers.GasLexer()
        else:
            lexer = pygments.lexers.get_lexer_for_filename(hint)

        formatter = pygments.formatters.TerminalFormatter()

        return pygments.highlight(source, lexer, formatter)

except ImportError:

    def syntax_highlight(source, hint):
        return source + "\n"


class Assembly(Module):
    """Print assembly information"""

    ORDER = 200

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame = None  # type: gdb.Frame | None
        self.instructions = []  # type: list[Instruction]

    def render(self, width, hight, write):
        inferior = gdb.selected_inferior()
        frame = gdb.selected_frame()
        pc = fetch_pc(frame)

        if frame != self.frame:
            self.fetch_new_instructions(frame)

        self.frame = frame

        try:
            self.flavor = str(gdb.parameter("disassembly-flavor"))
        except:
            self.flavor = "att"

        location = self.find_pc_location(pc)

        before = self.options["instructions-before"].value
        after = self.options["instructions-after"].value

        self.max_opcode_width = self.get_max_opcode_width(location)
        self.max_offset_width = self.get_max_offset_width(location)

        padding_before = max(before - location, 0)
        padding_after = max(location + after + 1 - len(self.instructions), 0)

        self.write_padding(padding_before, write)
        self.write_instructions(
            location - before + padding_before, location, inferior, write
        )
        self.write_current_instruction(inferior, self.instructions[location], write)
        self.write_instructions(
            location + 1, location + after - padding_after + 1, inferior, write
        )
        self.write_padding(padding_after, write)

    def fetch_new_instructions(self, frame):  # type: (gdb.Frame) -> None
        disassembly = gdb.execute("disassemble", to_string=True)

        if disassembly is None:
            raise Exception("Failed to disassemble current frame")

        function = frame.function()

        if function is None:
            lines = disassembly.split("\n")

            match = re.search(r"(\w+):$", lines[0])

            if match:
                self.function_name = match.group(1)
            else:
                self.function_name = "?"

            match = re.search(r"0x([0-9a-fA-F]+)", lines[1])

            if match:
                self.function_address = int(match.group(1), 16)

            count = len(lines) - 3
        else:
            self.function_name = function.name
            self.function_address = int(
                function.value().address.cast(gdb.lookup_type("unsigned long"))
            )
            count = disassembly.count("\n") - 2

        self.instructions = fetch_instructions(
            frame.architecture(), self.function_address, count
        )

    def find_pc_location(self, pc):  # type: (int) -> int
        for i, instruction in enumerate(self.instructions):
            if instruction["addr"] == pc:
                return i

        return -1

    def get_max_opcode_width(self, location):  # type: (int) -> int
        start = max(location - self.options["instructions-before"].value, 0)
        end = min(
            location + self.options["instructions-after"].value + 1,
            len(self.instructions),
        )

        result = 0

        for i in range(start, end):
            result = max(result, self.instructions[i]["length"])

        return 3 * result - 1

    def get_max_offset_width(self, location):  # type: (int) -> int
        last = min(
            location + self.options["instructions-after"].value,
            len(self.instructions) - 1,
        )
        offset = str(self.instructions[last]["addr"] - self.function_address)
        return len(offset)

    def write_padding(self, count, write):
        padding = "..."
        for _ in range(count):
            write(self.o["text-secondary"].value)
            write(
                f"{padding:<16}  {padding:<{self.max_opcode_width}}  "
                f"{padding:<{len(self.function_name) + self.max_offset_width + 1}}  {padding}\n"
            )

    def write_instruction(self, inferior, instruction, write):
        address = instruction["addr"]
        length = instruction["length"]
        opcode = inferior.read_memory(address, length)
        offset = address - self.function_address
        assembly = syntax_highlight(instruction["asm"], self.flavor)

        write(
            f"{self.o['text-secondary']}{address:#016x}{RESET_COLOR}  "
            f"{opcode.hex(' ', 1):<{self.max_opcode_width}}{RESET_COLOR}  "
            f"{self.o['text-secondary']}{self.function_name}+{offset:<{self.max_offset_width}}{RESET_COLOR}  "
            f"{assembly}"
        )

    def write_current_instruction(self, inferior, instruction, write):
        address = instruction["addr"]
        length = instruction["length"]
        opcode = inferior.read_memory(address, length)
        offset = address - self.function_address
        assembly = syntax_highlight(instruction["asm"], self.flavor)

        write(
            f"{self.o['text-secondary']}{FONT_BOLD}{address:#016x}{RESET_COLOR}  "
            f"{self.o['text-highlight']}{FONT_BOLD}{opcode.hex(' ', 1):<{self.max_opcode_width}}{RESET_COLOR}  "
            f"{self.o['text-secondary']}{FONT_BOLD}{self.function_name}+{offset:<{self.max_offset_width}}{RESET_COLOR}  "
            f"{FONT_BOLD}{assembly}"
        )

    def write_instructions(self, start, end, inferior, write):
        for i in range(start, end):
            self.write_instruction(inferior, self.instructions[i], write)

    @cached_property
    def options(self):  # type: () -> AssemblyOptions
        return {
            "instructions-before": IntOption(
                "Number of instructions displayed before the program counter", 5
            ),
            "instructions-after": IntOption(
                "Number of instructions displayed after the program counter", 5
            ),
        }
