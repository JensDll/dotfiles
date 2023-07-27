from functools import cached_property
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.utils import RESET_COLOR, fetch_instructions, fetch_pc

from .module import Module

if TYPE_CHECKING:
    from .alignment import AlignmentOptions


class Alignment(Module):
    """Print 64-byte-block formatted memory to see if instructions cross block boundaries"""

    ORDER = 100
    BLOCK_SIZE = 64

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        frame = gdb.selected_frame()
        pc = fetch_pc(frame)

        residue_class = pc & (self.BLOCK_SIZE - 1)
        self.start = pc - residue_class
        self.end = self.start + self.BLOCK_SIZE

    def render(self, width, height, write):
        if width < 115:
            per_row = 16
        else:
            per_row = 32

        padding = per_row * 2

        inferior = gdb.selected_inferior()
        frame = gdb.selected_frame()
        architecture = frame.architecture()
        pc = fetch_pc(frame)

        instruction_length = fetch_instructions(architecture, pc)[0]["length"]

        memory = inferior.read_memory(
            self.start - padding, self.BLOCK_SIZE + padding * 2
        )

        instruction_start = padding + (pc & (self.BLOCK_SIZE - 1))
        instruction_end = instruction_start + instruction_length

        color = RESET_COLOR

        for i, byte in enumerate(memory):
            if i == padding:
                write("\n")
            elif i == padding + self.BLOCK_SIZE:
                write("\n")

            if i == instruction_start:
                color = self.o["text-highlight"].value
            elif i == instruction_end:
                color = RESET_COLOR

            if i & (per_row - 1) == 0:
                write(self.o["text-secondary"].value)
                write(f"{pc + i - instruction_start:#016x} ")
                write(color)

            write(f" {color}{byte.hex()}")  # type: ignore

            if (i + 1) & (per_row - 1) == 0:
                write("\n")

        if pc + instruction_length >= self.end:
            self.start += self.BLOCK_SIZE
            self.end += self.BLOCK_SIZE

    @cached_property
    def options(self):  # type: () -> AlignmentOptions
        return {}
