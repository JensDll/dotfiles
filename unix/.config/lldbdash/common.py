import typing

import lldb

Output = lldb.SBStream | lldb.SBCommandReturnObject

FileStreamsEntry = typing.TypedDict(
    "FileStreamsEntry", {"stream": lldb.SBStream, "num_writers": int}
)
file_streams: dict[str, FileStreamsEntry] = dict()

RESET_COLOR = "\033[0m"
FONT_BOLD = "\033[1m"
FONT_UNDERLINE = "\033[4m"


def is_file(output: str):
    return output != "0"
