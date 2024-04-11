import typing

from gdbdash.commands import BoolOption, IntOption

from .module import Module

AssemblyOptions = typing.TypedDict(
    "AssemblyOptions",
    {
        "instructions-before": IntOption,
        "instructions-after": IntOption,
        "short-function": BoolOption,
        "no-function": BoolOption,
    },
)

class Assembly(Module):
    pass
