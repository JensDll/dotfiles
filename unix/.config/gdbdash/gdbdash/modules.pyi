from abc import abstractmethod

from .commands import Command, Configurable, Outputable, Togglable
from .utils import WriteWrapper

class Module(Command, Togglable, Configurable, Outputable):
    def __init__(
        self,
        /,
        dashboard_options,
        **kwargs,
    ): ...
    @abstractmethod
    def render(self, width: int, height, write: WriteWrapper): ...
    def divider(self, width, height, write: WriteWrapper): ...
