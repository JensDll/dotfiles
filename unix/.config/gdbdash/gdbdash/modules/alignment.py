from functools import cached_property
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.commands import IntOption
from gdbdash.utils import RESET_COLOR, fetch_instructions, fetch_pc

from .module import Module

if TYPE_CHECKING:
    from .alignment import AlignmentOptions


class Alignment(Module):
    """Print block formatted memory around the program counter"""

    ORDER = 100

    def render(self, width, height, write):
        block_size = self.options["block-size"].value

        blocks_per_row = max((width - 20) // ((block_size * 3) + 1), 1)
        per_row = blocks_per_row * block_size

        inferior = gdb.selected_inferior()
        frame = gdb.selected_frame()
        architecture = frame.architecture()
        pc = fetch_pc(frame)

        residue_class = pc % per_row

        instruction_length = fetch_instructions(architecture, pc)[0]["length"]
        instruction_start = per_row + residue_class
        instruction_end = instruction_start + instruction_length

        memory = inferior.read_memory(pc - residue_class - per_row, per_row * 3)

        color = RESET_COLOR

        for row in range(0, per_row * 3, per_row):
            address = pc + row - instruction_start
            write(f"{self.o['text-secondary']}{address:#016x}{color}")
            for block in range(0, per_row, block_size):
                write(f"{RESET_COLOR} {color}")
                for col in range(block_size):
                    idx = row + block + col
                    if idx == instruction_start:
                        color = self.o["text-highlight"].value
                    elif idx == instruction_end:
                        color = RESET_COLOR
                    # In reality is bytes and not int
                    write(f" {color}{memory[idx].hex()}")  # type: ignore
            write("\n")

    @cached_property
    def options(self):  # type: () -> AlignmentOptions
        return {
            "block-size": IntOption(
                "The block size in byte which are grouped together", 16
            )
        }
