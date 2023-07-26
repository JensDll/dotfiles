from typing import TypedDict

from .commands import BoolOption, FileDescriptorOrPath, StrOption
from .modules import Module

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
