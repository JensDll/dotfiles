from typing import Protocol

from gdbdash.dashboard import DashboardModulesDict
from gdbdash.utils import FileDescriptorOrPath

from .command import CommandProtocol

class OutputableProtocol(CommandProtocol, Protocol):
    dashboard_modules_dict: DashboardModulesDict
    output: FileDescriptorOrPath
    def on_output_changed(self, old_output: FileDescriptorOrPath) -> None: ...

class Outputable:
    dashboard_modules_dict: DashboardModulesDict
    output: FileDescriptorOrPath
    def on_output_changed(self, old_output: FileDescriptorOrPath) -> None: ...
