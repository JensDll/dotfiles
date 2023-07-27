from abc import ABCMeta, abstractmethod
from typing import Protocol

from .command import CommandProtocol

class TogglableProtocol(CommandProtocol, Protocol):
    enabled: bool
    def enable(self) -> None: ...
    def disable(self) -> None: ...

class Togglable(metaclass=ABCMeta):
    enabled: bool
    def __init__(self, /, **kwargs) -> None: ...
    @abstractmethod
    def enable(self) -> None: ...
    @abstractmethod
    def disable(self) -> None: ...
