from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.utils import GdbBool, complete

from .command import Command

if TYPE_CHECKING:
    from .enable import TogglableProtocol


class Togglable:
    def __init__(
        self,  # type: TogglableProtocol
        /,
        **kwargs,
    ):
        if not isinstance(self, Command):
            raise TypeError(f"{self} must be a {Command}")

        super().__init__(**kwargs)

        self.enabled = False
        self.enable()

        EnableCommand(self)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class EnableCommand(Command):
    descriptor = GdbBool()

    def __init__(
        self,
        togglable,  # type: TogglableProtocol
    ):
        super().__init__(
            command_name=f"{togglable.command_name} -enable",
            command_class=gdb.COMMAND_USER,
            command_prefix=False,
            command_doc=f"Enable or disable this module",
        )

        self.togglable = togglable

    def invoke(self, arg, from_tty):
        super().dont_repeat()
        argv = gdb.string_to_argv(arg)

        if len(argv) == 0:
            self.togglable.stdout(
                f"Is currently {self.togglable.enabled and 'enabled' or 'disabled'}"
            )
            return

        self.descriptor = argv[0]

        if self.descriptor:
            self.togglable.enable()
        else:
            self.togglable.disable()

    def complete(self, text, word):
        return complete(word, GdbBool.CHOICES)
