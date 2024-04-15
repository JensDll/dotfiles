import os

from lldbdash.commands import Command

StrOrBytesPath = str | bytes | os.PathLike[str] | os.PathLike[bytes]
FileDescriptorOrPath = int | StrOrBytesPath

Settings = dict[str, Command]
