from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

import gdb

from .command import Command
from .configure import Configurable

if TYPE_CHECKING:
    from .dump import DumpableProtocol


class Dumpable(metaclass=ABCMeta):
    def __init__(
        self,  # type: DumpableProtocol
        **kwargs,
    ):
        if not isinstance(self, Configurable):
            raise TypeError(f"A dumpable class must be configurable")

        super().__init__(**kwargs)

        DumpCommand(self)
        LoadCommand(self)

    @abstractmethod
    def dump(self, config_path):
        pass

    @abstractmethod
    def load(self, config_path):
        pass


class DumpCommand(Command):
    def __init__(
        self, dumpable  # type: DumpableProtocol
    ):
        super().__init__(
            command_name=f"{dumpable.command_name} -dump",
            command_class=gdb.COMMAND_USER,
            command_completer_class=gdb.COMPLETE_FILENAME,
            command_prefix=True,
            command_doc="Dump the current configuration to a file",
        )

        self.dumpable = dumpable

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        path = argv[0] if len(argv) > 0 else "gdbdash.json"
        self.dumpable.dump(path)


class LoadCommand(Command):
    def __init__(
        self, dumpable  # type: DumpableProtocol
    ):
        super().__init__(
            command_name=f"{dumpable.command_name} -load",
            command_class=gdb.COMMAND_USER,
            command_completer_class=gdb.COMPLETE_FILENAME,
            command_prefix=True,
            command_doc="Load a configuration from a file",
        )

        self.dumpable = dumpable

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        path = argv[0] if len(argv) > 0 else "gdbdash.json"
        self.dumpable.load(path)
