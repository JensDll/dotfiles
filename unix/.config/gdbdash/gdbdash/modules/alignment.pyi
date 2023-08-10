import typing

from gdbdash.commands import IntOption

AlignmentOptions = typing.TypedDict("AlignmentOptions", {"block-size": IntOption})

class Alignment:
    pass
