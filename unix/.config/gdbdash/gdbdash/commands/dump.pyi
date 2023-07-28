from abc import ABCMeta, abstractmethod
from typing import Protocol

from gdbdash.utils import FileDescriptorOrPath

from .configure import ConfigurableProtocol

class DumpableProtocol(ConfigurableProtocol, Protocol):
    def dump(self, config_path: FileDescriptorOrPath) -> None: ...
    def load(self, config_path: FileDescriptorOrPath) -> None: ...

class Dumpable:
    def dump(self, path: FileDescriptorOrPath) -> None: ...
    def load(self, config_path: FileDescriptorOrPath) -> None: ...
