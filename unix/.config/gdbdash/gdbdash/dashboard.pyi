from typing import TypedDict

from gdbdash.commands import BoolOption, StrOption
from gdbdash.modules import Module
from gdbdash.utils import FileDescriptorOrPath

DashboardOptions = TypedDict(
    "DashboardOptions",
    {
        "text-highlight": StrOption,
        "text-secondary": StrOption,
        "text-divider": StrOption,
        "text-divider-title": StrOption,
        "divider-fill-char": StrOption,
        "show-divider": BoolOption,
    },
)

DashboardModulesDict = dict[FileDescriptorOrPath, list[Module]]

class Dashboard:
    pass
