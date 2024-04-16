from abc import abstractmethod
from typing import TYPE_CHECKING

import gdb
from gdbdash.commands import Command, Configurable, Orderable, Outputable, Togglable
from gdbdash.utils import RESET_COLOR

if TYPE_CHECKING:
    from gdbdash.dashboard import DashboardModulesDict, DashboardOptions


class Module(Command, Togglable, Configurable, Outputable, Orderable):
    def __init__(
        self,
        /,
        options,  # type: DashboardOptions
        outputables,  # type: DashboardModulesDict
        **kwargs,
    ):
        self.o = options
        self.outputables = outputables
        self.name = self.__class__.__name__
        self.normalized_name = self.name.lower()

        self.frame = gdb.selected_frame()
        self.architecture = self.frame.architecture()
        self.uint64_t = self.architecture.integer_type(64, False)

        super().__init__(
            command_name=f"dashboard {self.normalized_name}",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
            command_doc=self.__doc__,
            **kwargs,
        )

    def on_order_changed(self):
        self.outputables[self.output].sort(key=lambda module: module.ORDER)

    def divider(self, width, height, write):
        if not self.o["show-divider"].value:
            write("\n")
            return

        before = self.o["divider-fill-char"].value * (width >> 4)
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

    @abstractmethod
    def render(self, width, height, write):
        pass
