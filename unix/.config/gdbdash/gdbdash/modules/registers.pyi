import typing

from gdbdash.commands import BoolOption

RegisterOptions = typing.TypedDict(
    "RegisterOptions",
    {
        "show-32": BoolOption,
        "show-decimal": BoolOption,
        "show-segment": BoolOption,
        "show-eflags": BoolOption,
        "show-mxcsr": BoolOption,
    },
)

class Registers:
    pass
