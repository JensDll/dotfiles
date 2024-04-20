import dataclasses
import os
import typing

import lldb
import lldb.utils
import lldbdash.commands
from lldbdash.common import FONT_BOLD, RESET_COLOR

from .on_change_output import on_change_output


class Instruction:
    @dataclasses.dataclass
    class PrintDimensions:
        name_width: int
        opcode_width: int
        mnemonic_width: int

    def __init__(
        self,
        target: lldb.SBTarget,
        symbol: lldb.SBSymbol,
        instruction: lldb.SBInstruction,
    ):
        self.symbol: lldb.SBSymbol = symbol

        addr: lldb.SBAddress = instruction.GetAddress()
        self.addr: int = addr.GetLoadAddress(target)

        self.mnemonic: str = instruction.GetMnemonic(target)
        self.operands: str = instruction.GetOperands(target)

        comment: str = instruction.GetComment(target)
        self.comment: str = f" ; {comment}" if comment else ""

        self.size: int = instruction.GetByteSize()
        error = lldb.SBError()
        opcode: bytearray = target.ReadMemory(addr, self.size, error)
        self.opcode = " ".join(f"{byte:02X}" for byte in opcode)

        self.name: str = symbol.GetName()
        self.offset: int = self.addr - symbol.GetStartAddress().GetLoadAddress(target)

    @classmethod
    def list(cls, symbol: lldb.SBSymbol, target: lldb.SBTarget):
        instructions = symbol.GetInstructions(
            target, AssemblyModule.settings["flavor"].value
        )
        return list(map(lambda inst: cls(target, symbol, inst), instructions))

    def print(
        self,
        stream: lldb.SBStream,
        dim: PrintDimensions,
    ):
        name = self.get_name()
        stream.Print(
            f"{self.addr:#0x}  {name:<{dim.name_width}}  {self.opcode:<{dim.opcode_width}}  "
            f"{self.mnemonic:<{dim.mnemonic_width}} {self.operands}{self.comment}\n"
        )

    def get_name(self):
        return f"{self.name}+{self.offset}"


class InstructionPrinter:
    _frame: lldb.SBFrame | None = None
    _instance: "InstructionPrinter"

    def __init__(self, frame: lldb.SBFrame, target: lldb.SBTarget):
        self.frame = frame
        self.target = target
        self.instructions = Instruction.list(frame.GetSymbol(), target)

    @classmethod
    def new_or_cached(cls, frame: lldb.SBFrame, target: lldb.SBTarget):
        if cls._frame != frame:
            cls._instance = cls(frame, target)
            cls._frame = frame
        return cls._instance

    def find_pc_idx(self):
        pc: int = self.frame.GetPC()
        for i, inst in enumerate(self.instructions):
            if inst.addr == pc:
                return i
        raise Exception("Program counter is not part of the current instructions")

    def find_print_dimensions(self, start: int, end: int):
        name_width = opcode_width = mnemonic_width = 0

        for i in range(start, end):
            instruction = self.instructions[i]
            name = instruction.get_name()
            name_width = max(name_width, len(name))
            opcode_width = max(opcode_width, len(instruction.opcode))
            mnemonic_width = max(mnemonic_width, len(instruction.mnemonic))

        return Instruction.PrintDimensions(
            name_width=name_width,
            opcode_width=opcode_width,
            mnemonic_width=mnemonic_width,
        )

    def print(self, stream: lldb.SBStream):
        pc_idx = self.find_pc_idx()

        pc_idx = self.fetch_blocks_start(pc_idx)
        self.fetch_blocks_end(pc_idx)

        before = AssemblyModule.settings["instructions-before"].value
        after = AssemblyModule.settings["instructions-after"].value

        padding_before = max(before - pc_idx, 0)
        padding_after = max(pc_idx + after + 1 - len(self.instructions), 0)

        start = pc_idx - before + padding_before
        end = pc_idx + after - padding_after + 1

        dimensions = self.find_print_dimensions(start, end)

        self.print_instructions(stream, dimensions, start, pc_idx)
        stream.Print(FONT_BOLD)
        self.instructions[pc_idx].print(stream, dimensions)
        stream.Print(RESET_COLOR)
        self.print_instructions(stream, dimensions, pc_idx + 1, end)

    def print_instructions(
        self,
        stream: lldb.SBStream,
        dimensions: Instruction.PrintDimensions,
        start: int,
        end: int,
    ):
        for i in range(start, end):
            self.instructions[i].print(stream, dimensions)

    def fetch_blocks_start(self, pc_idx: int):
        before = AssemblyModule.settings["instructions-before"].value - pc_idx

        while before > 0:
            addr: lldb.SBAddress = self.instructions[0].symbol.GetStartAddress()
            addr.SetLoadAddress(addr.GetLoadAddress(self.target) - 1, self.target)

            context: lldb.SBSymbolContext = self.target.ResolveSymbolContextForAddress(
                addr, lldb.eSymbolContextEverything
            )

            if not context.IsValid():
                break

            instructions = Instruction.list(context.GetSymbol(), self.target)

            if not instructions:
                break

            self.instructions = instructions + self.instructions

            pc_idx += len(instructions)
            before -= len(instructions)

        return pc_idx

    def fetch_blocks_end(self, pc_idx: int):
        after = (
            AssemblyModule.settings["instructions-after"].value
            - len(self.instructions)
            + pc_idx
            + 1
        )

        while after > 0:
            addr: lldb.SBAddress = self.instructions[-1].symbol.GetEndAddress()

            context: lldb.SBSymbolContext = self.target.ResolveSymbolContextForAddress(
                addr, lldb.eSymbolContextEverything
            )

            if not context.IsValid():
                break

            instructions = Instruction.list(context.GetSymbol(), self.target)

            if not instructions:
                break

            self.instructions = self.instructions + instructions

            after -= len(instructions)


class AssemblyModule:
    Settings = typing.TypedDict(
        "Settings",
        {
            "instructions-before": lldbdash.commands.IntCommand,
            "instructions-after": lldbdash.commands.IntCommand,
            "flavor": lldbdash.commands.StrCommand,
        },
    )

    name = "assembly"

    settings: Settings = {
        "instructions-before": lldbdash.commands.IntCommand(
            10, help="Number of instructions before the program counter."
        ),
        "instructions-after": lldbdash.commands.IntCommand(
            10, help="Number of instructions after the program counter."
        ),
        "flavor": lldbdash.commands.StrCommand("intel", help="The disassembly flavor."),
    }
    output = lldbdash.commands.StrCommand(
        "0",
        help="The render location of the assembly module.",
        on_change=on_change_output,
    )
    enabled = lldbdash.commands.ToggleCommand(
        True,
        enable_help="Enable the assembly module",
        disable_help="Disable the assembly module",
    )

    @staticmethod
    def render(
        size: os.terminal_size, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream
    ):
        target: lldb.SBTarget = exe_ctx.GetTarget()
        frame: lldb.SBFrame = exe_ctx.GetFrame()
        printer = InstructionPrinter.new_or_cached(frame, target)
        printer.print(stream)
