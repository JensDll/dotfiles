from functools import cached_property
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.commands import IntOption
from gdbdash.utils import RESET_COLOR, fetch_instructions, fetch_pc

from .module import Module

if TYPE_CHECKING:
    from typing import Any

    from .alignment import AlignmentOptions


class Alignment(Module):
    """Print block formatted memory around the program counter"""

    ORDER = 100

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

    def render(self, width, height, write):
        block_size = self.options["block-size"].value

        blocks_per_row = max((width - 20) // (block_size * 3), 1)
        per_row = blocks_per_row * block_size

        inferior = gdb.selected_inferior()
        frame = gdb.selected_frame()
        architecture = frame.architecture()
        pc = fetch_pc(frame)

        instruction_length = fetch_instructions(architecture, pc)[0]["length"]

        residue_class = pc & (per_row - 1)
        start = pc - residue_class

        instruction_start = per_row + (pc & (per_row - 1))
        instruction_end = instruction_start + instruction_length

        memory = inferior.read_memory(start - per_row, per_row * 3)

        color = RESET_COLOR

        for i in range(0, per_row * 3, per_row):
            write(self.o["text-secondary"].value)
            write(f"{pc + i - instruction_start:#016x}")
            write(color)

            for j in range(0, per_row, block_size):
                write(" ")

                for k in range(block_size):
                    idx = i + j + k
                    byte = memory[idx]  # type: Any

                    if idx == instruction_start:
                        color = self.o["text-highlight"].value
                    elif idx == instruction_end:
                        color = RESET_COLOR

                    write(f" {color}{byte.hex()}")

            write("\n")

    @cached_property
    def options(self):  # type: () -> AlignmentOptions
        return {
            "block-size": IntOption("The block size in byte to be printed together", 16)
        }
