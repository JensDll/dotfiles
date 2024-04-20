import os
import typing

from lldb import SBStream
from lldbdash.commands import Command

StrOrBytesPath = str | bytes | os.PathLike[str] | os.PathLike[bytes]
FileDescriptorOrPath = int | StrOrBytesPath

Settings = dict[str, Command]

FileStreamsEntry = typing.TypedDict(
    "FileStreamsEntry", {"stream": SBStream, "num_writers": int}
)
file_streams: dict[str, FileStreamsEntry] = dict()

RESET_COLOR = "\033[0m"
FONT_BOLD = "\033[1m"
FONT_UNDERLINE = "\033[4m"
