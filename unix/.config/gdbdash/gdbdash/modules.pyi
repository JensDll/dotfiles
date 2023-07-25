from abc import abstractmethod
from typing import Final, TypedDict

from .commands import BoolOption, Command, Configurable, Outputable, Togglable
from .utils import WriteWrapper

class Module(Command, Togglable, Configurable, Outputable):
    ORDER: Final[int]
    def __init__(
        self,
        /,
        dashboard_options,
        **kwargs,
    ): ...
    @abstractmethod
    def render(self, width: int, height, write: WriteWrapper): ...
    def divider(self, width, height, write: WriteWrapper): ...

AssemblyOptions = TypedDict(
    "AssemblyOptions",
    {
        "show-function": BoolOption,
    },
)

AlignmentOptions = TypedDict(
    "AlignmentOptions",
    {},
)

RegistryOptions = TypedDict(
    "RegistryOptions",
    {},
)
