from abc import abstractmethod
from typing import ClassVar

from gdbdash.commands import Command, Configurable, Outputable, Togglable
from gdbdash.dashboard import DashboardModulesDict, DashboardOptions
from gdbdash.utils import WriteWrapper

class Module(Command, Togglable, Configurable, Outputable):
    ORDER: ClassVar[int]
    o: DashboardOptions
    name: str
    lower_name: str
    def __init__(
        self, /, options: DashboardOptions, outputables: DashboardModulesDict, **kwargs
    ): ...
    @abstractmethod
    def render(self, width: int, height, write: WriteWrapper): ...
    def divider(self, width, height, write: WriteWrapper): ...
