from typing import TypedDict

import gdb
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
    options: DashboardOptions
    modules_dict: DashboardModulesDict
    def on_order_changed(self) -> None: ...
