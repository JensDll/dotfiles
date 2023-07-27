import typing

from gdbdash.commands import IntOption

from .module import Module

AssemblyOptions = typing.TypedDict(
    "AssemblyOptions",
    {"instructions-before": IntOption, "instructions-after": IntOption},
)

class Assembly(Module):
    pass
