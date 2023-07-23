import abc
import functools
import itertools
import os
import typing

import gdb  # pyright: ignore [reportMissingModuleSource]
import gdbdash.commands
import gdbdash.utils

COLOR_BLUE = "\033[30;1;34m"
COLOR_GREEN = "\033[30;1;32m"
COLOR_RESET = "\033[0m"


class Module(
    gdbdash.commands.Togglable, gdbdash.commands.Configurable, gdbdash.commands.Command
):
    def __init__(self):
        self.output = gdb.STDOUT
        self.inferior = gdb.selected_inferior()
        self.frame = gdb.selected_frame()
        self.architecture = self.frame.architecture()
        self.pc = fetch_pc(self.frame)
        self.name = self.__class__.__name__.lower()
        self.doc = self.__doc__ or "(no documentation)"
        super().__init__(
            command_name=f"dashboard {self.name}",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
        )

    def write(self, string: str):
        gdb.write(string, self.output)

    @abc.abstractmethod
    def render(self, width: int, height: int) -> None:
        pass


class Alignment(Module):
    """Print 64-byte block formatted memory"""

    BLOCK_SIZE = 64

    def __init__(self):
        super().__init__()
        self.per_row = 32
        self.padding = self.per_row * 2
        residue_class = self.pc & (self.BLOCK_SIZE - 1)
        self.start = self.pc - residue_class
        self.end = self.start + self.BLOCK_SIZE

    @functools.cached_property
    def options(self) -> gdbdash.commands.Options:
        return {}

    def render(self, width, height) -> None:
        pc = fetch_pc(self.frame)

        instruction_length = fetch_instructions(self.architecture, pc)[0]["length"]

        memory = self.inferior.read_memory(
            self.start - self.padding, self.BLOCK_SIZE + self.padding * 2
        )

        instruction_start = self.padding + (pc & (self.BLOCK_SIZE - 1))
        instruction_end = instruction_start + instruction_length

        color: typing.Union[None, str] = None

        for i, byte in enumerate(typing.cast(typing.Iterable[bytes], memory)):
            if i == self.padding:
                self.write("\n")
            elif i == self.padding + self.BLOCK_SIZE:
                self.write("\n")

            if i == instruction_start:
                self.write(COLOR_GREEN)
                color = COLOR_GREEN
            elif i == instruction_end:
                self.write(COLOR_RESET)
                color = None

            if i & (self.per_row - 1) == 0:
                self.write(COLOR_RESET)
                self.write(f"{pc + i - instruction_start:#016x}  ")
                if color:
                    self.write(color)

            self.write(byte.hex() + " ")

            if (i + 1) & (self.per_row - 1) == 0:
                self.write("\n")

        if pc + instruction_length >= self.end:
            self.start += self.BLOCK_SIZE
            self.end += self.BLOCK_SIZE


class Assembly(Module):
    """Print assembly information"""

    def __init__(self):
        super().__init__()

    @functools.cached_property
    def options(self) -> gdbdash.commands.Options:
        return {
            "opcodes": gdbdash.commands.BoolOption(
                "Show hexadecimal instruction next to assembly",
                value="on",
            ),
        }

    def render(self, width, height) -> None:
        pc = fetch_pc(self.frame)

        try:
            flavor = str(gdb.parameter("disassembly-flavor"))
        except:
            flavor = "att"

        instructions = fetch_instructions(self.architecture, pc, 6)

        func = self.frame.function()
        func_addr = int(func.value().address.cast(gdb.lookup_type("unsigned long")))

        max_instruction_width = (
            max(instruction["length"] for instruction in instructions) * 2
        )
        max_instruction_width += (
            (max_instruction_width // 2) + (max_instruction_width % 2) - 1
        )

        max_offset_width = len(str(instructions[-1]["addr"] - func_addr))

        addr = instructions[0]["addr"]
        length = instructions[0]["length"]
        asm = syntax_highlight(instructions[0]["asm"], flavor)
        instruction = self.inferior.read_memory(addr, length)
        offset = addr - func_addr

        self.write(
            f"{addr:#016x}  {COLOR_GREEN}{instruction.hex(' ', 1):<{max_instruction_width}}{COLOR_RESET}  {func}+{offset:<{max_offset_width}} {asm}"
        )

        for instruction in itertools.islice(instructions, 1, None):
            addr = instruction["addr"]
            length = instruction["length"]
            asm = syntax_highlight(instruction["asm"], flavor)
            memory = self.inferior.read_memory(addr, length)
            offset = addr - func_addr

            self.write(
                f"{addr:#016x}  {memory.hex(' ', 1):<{max_instruction_width}}  {func}+{offset:<{max_offset_width}} {asm}"
            )


class Registers(Module):
    """Print register information"""

    def __init__(self):
        super().__init__()

    @functools.cached_property
    def options(self) -> gdbdash.commands.Options:
        return {}

    def render(self, width, height) -> None:
        pass


def syntax_highlight(source: str, hint: str):
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


def fetch_pc(frame: gdb.Frame):
    return typing.cast(int, frame.pc())


class Instruction(typing.TypedDict):
    addr: int
    length: int
    asm: str


def fetch_instructions(architecture: gdb.Architecture, start_pc: int, count: int = 1):
    return typing.cast(
        typing.List[Instruction], architecture.disassemble(start_pc, count=count)
    )


def fetch_instructions_range(
    architecture: gdb.Architecture, start_pc: int, end_pc: int
):
    return typing.cast(
        typing.List[Instruction], architecture.disassemble(start_pc, end_pc=end_pc)
    )
