import typing

from gdbdash.commands import BoolOption

RegisterOptions = typing.TypedDict(
    "RegisterOptions",
    {
        "show-32": BoolOption,
        "show-decimal": BoolOption,
    },
)

class Registers:
    pass
