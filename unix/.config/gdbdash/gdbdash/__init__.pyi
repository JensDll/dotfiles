from typing import TypedDict

from .commands import FileDescriptorOrPath, StrOption
from .modules import Module

DashboardOptions = TypedDict(
    "DashboardOptions",
    {
        "text-highlight": StrOption,
        "text-divider": StrOption,
        "text-divider-title": StrOption,
        "text-100": StrOption,
        "text-200": StrOption,
        "divider-fill-char": StrOption,
    },
)

DashboardModulesDict = dict[FileDescriptorOrPath, list[Module]]
