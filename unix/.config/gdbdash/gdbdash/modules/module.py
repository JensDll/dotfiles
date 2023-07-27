from abc import abstractmethod
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.commands import Command, Configurable, Outputable, Togglable
from gdbdash.utils import RESET_COLOR

if TYPE_CHECKING:
    from gdbdash.dashboard import DashboardOptions


class Module(Command, Togglable, Configurable, Outputable):
    def __init__(
        self,
        /,
        dashboard_options,  # type: DashboardOptions
        **kwargs,
    ):
        self.o = dashboard_options
        self.name = self.__class__.__name__

        super().__init__(
            command_name=f"dashboard {self.name.lower()}",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
            command_doc=self.__doc__,
            **kwargs,
        )

    @abstractmethod
    def render(self, width, height, write):
        pass

    def divider(self, width, height, write):
        if not self.o["show-divider"].value:
            write("\n")
            return

        before = self.o["divider-fill-char"].value * (width // 16)
        name = f" {self.name} "
        after = self.o["divider-fill-char"].value * (width - len(before) - len(name))

        write(self.o["text-divider"].value)
        write(before)
        write(self.o["text-divider-title"].value)
        write(name)
        write(self.o["text-divider"].value)
        write(after)
        write(RESET_COLOR)
        write("\n")
