from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]

from .command import Command

if TYPE_CHECKING:
    from .order import OrderableProtocol


class Orderable:
    def __init__(
        self,  # type: OrderableProtocol
        **kwargs,
    ):
        if not isinstance(self, Command):
            raise TypeError(f"A orderable class must be a command")

        super().__init__(**kwargs)

        OrderCommand(self)

    def on_order_changed(self):
        pass


class OrderCommand(Command):
    def __init__(
        self, orderable  # type: OrderableProtocol
    ):
        super().__init__(
            command_name=f"{orderable.command_name} -order",
            command_class=gdb.COMMAND_USER,
            command_prefix=False,
            command_doc=f"Change the order in which this module's text appears in the output",
        )

        self.orderable = orderable

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)

        if len(argv) == 0:
            self.stdout(f'The current order is "{self.orderable.ORDER}"')
            return

        self.orderable.__class__.ORDER = int(argv[0])
        self.orderable.on_order_changed()
