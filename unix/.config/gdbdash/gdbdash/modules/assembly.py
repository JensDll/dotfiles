from functools import cached_property
from itertools import islice
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.commands import IntOption
from gdbdash.utils import RESET_COLOR, fetch_instructions, fetch_pc

from .module import Module

if TYPE_CHECKING:
    from gdbdash.utils import Instruction

    from .assembly import AssemblyOptions


class Assembly(Module):
    """Print assembly information"""

    ORDER = 1

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
            flavor = str(gdb.parameter("disassembly-flavor"))
        except:
            flavor = "att"

        location = self.find_pc_location(pc)

        before = self.options["before"].value
        after = self.options["after"].value

        max_opcode_width = self.get_max_opcode_width(location)
        max_offset_width = self.get_max_offset_width(location)

        padding_before = max(before - location, 0)
        padding_after = max(location + after + 1 - len(self.instructions), 0)

        self.write_padding(padding_before, write)
        self.write_instructions(
            location - before + padding_before,
            location,
            inferior,
            max_opcode_width,
            max_offset_width,
            flavor,
            write,
        )
        self.write_instruction(
            inferior,
            self.instructions[location],
            self.o["text-highlight"],
            max_opcode_width,
            max_offset_width,
            flavor,
            write,
        )
        self.write_instructions(
            location + 1,
            location + after - padding_after + 1,
            inferior,
            max_opcode_width,
            max_offset_width,
            flavor,
            write,
        )
        self.write_padding(padding_after, write)

    def fetch_new_instructions(self, frame):  # type: (gdb.Frame) -> None
        self.function = frame.function()
        self.function_address = int(
            self.function.value().address.cast(gdb.lookup_type("unsigned long"))
        )

        disassembly = gdb.execute("disassemble", to_string=True)

        if disassembly is None:
            return

        count = disassembly.count("\n") - 2

        self.instructions = fetch_instructions(
            frame.architecture(), self.function_address, count
        )

    def get_max_opcode_width(self, location):  # type: (int) -> int
        start = max(location - self.options["before"].value, 0)
        end = min(location + self.options["after"].value + 1, len(self.instructions))

        result = 0

        for i in range(start, end):
            result = max(result, self.instructions[i]["length"])

        return 2 * result + result - 1

    def get_max_offset_width(self, location):  # type: (int) -> int
        last = min(location + self.options["after"].value, len(self.instructions) - 1)
        offset = str(self.instructions[last]["addr"] - self.function_address)
        return len(offset)

    def find_pc_location(self, pc):  # type: (int) -> int
        for i, instruction in enumerate(self.instructions):
            address = instruction["addr"]
            if instruction["addr"] == pc:
                return i

        return -1

    def write_padding(self, end, write):
        for _ in range(end):
            write(self.o["text-secondary"].value)
            write(f"{0:#016x}  ...\n")

    def write_instruction(
        self,
        inferior,
        instruction,
        opcode_color,
        max_opcode_width,
        max_offset_width,
        flavor,
        write,
    ):
        address = instruction["addr"]
        length = instruction["length"]
        opcode = inferior.read_memory(address, length)
        offset = address - self.function_address
        assembly = syntax_highlight(instruction["asm"], flavor)

        write(
            f"{self.o['text-secondary']}{address:#016x}{RESET_COLOR}  "
            f"{opcode_color}{opcode.hex(' ', 1):<{max_opcode_width}}{RESET_COLOR}  "
            f"{self.o['text-secondary']}{self.function}+{offset:<{max_offset_width}}{RESET_COLOR}  "
            f"{assembly}"
        )

    def write_instructions(
        self,
        start,
        end,
        inferior,
        max_opcode_width,
        max_offset_width,
        flavor,
        write,
    ):
        for i in range(start, end):
            self.write_instruction(
                inferior,
                self.instructions[i],
                RESET_COLOR,
                max_opcode_width,
                max_offset_width,
                flavor,
                write,
            )

    @cached_property
    def options(self):  # type: () -> AssemblyOptions
        return {
            "before": IntOption("", 4),
            "after": IntOption("", 4),
        }


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


#     def _render(self, width, height, write):
#         inferior = gdb.selected_inferior()
#         frame = gdb.selected_frame()
#         architecture = frame.architecture()
#         pc = fetch_pc(frame)

#         instructions = fetch_instructions(architecture, pc, 6)

#         max_instruction_width = (
#             max(instruction["length"] for instruction in instructions) * 2
#         )
#         max_instruction_width += (
#             (max_instruction_width // 2) + (max_instruction_width % 2) - 1
#         )

#         try:
#             flavor = str(gdb.parameter("disassembly-flavor"))
#         except:
#             flavor = "att"

#         function = frame.function()
#         function_address = int(
#             function.value().address.cast(gdb.lookup_type("unsigned long"))
#         )

#         max_offset_width = len(str(instructions[-1]["addr"] - function_address))

#         self.write_line(
#             instruction=instructions[0],
#             max_instruction_width=max_instruction_width,
#             flavor=flavor,
#             opcode_color=self.o["text-highlight"].value,
#             inferior=inferior,
#             write=write,
#             function=function,
#             function_address=function_address,
#             max_offset_width=max_offset_width,
#         )

#         for instruction in islice(instructions, 1, None):
#             self.write_line(
#                 instruction=instruction,
#                 max_instruction_width=max_instruction_width,
#                 flavor=flavor,
#                 opcode_color=RESET_COLOR,
#                 inferior=inferior,
#                 write=write,
#                 function=function,
#                 function_address=function_address,
#                 max_offset_width=max_offset_width,
#             )
