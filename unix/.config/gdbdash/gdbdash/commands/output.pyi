from typing import Protocol

from gdbdash.dashboard import DashboardModulesDict
from gdbdash.utils import FileDescriptorOrPath

from .command import CommandProtocol

class OutputableProtocol(CommandProtocol, Protocol):
    outputables: DashboardModulesDict
    output: FileDescriptorOrPath
    def on_output_changed(self, old_output: FileDescriptorOrPath) -> None: ...

class Outputable:
    outputables: DashboardModulesDict
    output: FileDescriptorOrPath
    def on_output_changed(self, old_output: FileDescriptorOrPath) -> None: ...
