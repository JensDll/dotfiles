import typing

import lldb

FileStreamsEntry = typing.TypedDict(
    "FileStreamsEntry", {"stream": lldb.SBStream, "num_writers": int}
)
g_file_streams: dict[str, FileStreamsEntry] = dict()
