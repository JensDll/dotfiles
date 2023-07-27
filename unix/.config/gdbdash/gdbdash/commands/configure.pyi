from abc import ABCMeta, abstractmethod
from typing import Protocol

from .command import CommandProtocol
from .options import Options

class ConfigurableProtocol(CommandProtocol, Protocol):
    options: Options

class Configurable(metaclass=ABCMeta):
    def __init__(self, /, **kwargs) -> None: ...
    @property
    @abstractmethod
    def options(self) -> Options: ...
