import typing

from gdbdash.commands import IntOption

from .module import Module

AssemblyOptions = typing.TypedDict(
    "AssemblyOptions", {"before": IntOption, "after": IntOption}
)

class Assembly(Module):
    pass
