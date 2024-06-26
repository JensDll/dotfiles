from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

import gdb
from gdbdash.utils import GdbBool, GdbInt, complete

from .command import Command

if TYPE_CHECKING:
    from .configure import ConfigurableProtocol, Option


@dataclass
class BoolOption:
    doc: str
    value: GdbBool = GdbBool()
    choices: Sequence[str] = GdbBool.CHOICES

    def __str__(self):
        return str(self.value)


@dataclass
class IntOption:
    doc: str
    value: GdbInt = GdbInt()
    choices: int = gdb.COMPLETE_NONE

    def __str__(self):
        return str(self.value)


@dataclass
class StrOption:
    doc: str
    value: str
    choices: int = gdb.COMPLETE_NONE

    def __str__(self):
        return self.value


class Configurable(metaclass=ABCMeta):
    def __init__(
        self,  # type: ConfigurableProtocol
        /,
        **kwargs,
    ):
        if not isinstance(self, Command):
            raise TypeError(f"A configurable class must be a command")

        super().__init__(**kwargs)

        ConfigureCommand(self)

    @property
    @abstractmethod
    def options(self):
        pass


class ConfigureCommand(Command):
    def __init__(
        self,
        configurable,  # type: ConfigurableProtocol
    ):
        super().__init__(
            command_name=f"{configurable.command_name} -configure",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
            command_doc="Configure the options of this module",
        )

        self.commands = [
            ConfigureOptionCommand(
                command_name=f"{self.command_name} {option_name}",
                option_name=option_name,
                option=option,
            )
            for option_name, option in configurable.options.items()
        ]

    def invoke(self, arg, from_tty):
        for command in self.commands:
            command.invoke("", from_tty)


class ConfigureOptionCommand(Command):
    def __init__(
        self,
        /,
        command_name,  # type: str
        option_name,  # type: str
        option,  # type: Option
    ):
        super().__init__(
            command_name=command_name,
            command_class=gdb.COMMAND_USER,
            command_prefix=False,
            command_doc=option.doc,
        )

        self.option_name = option_name
        self.option = option

    def invoke(self, arg, from_tty):
        super().dont_repeat()
        argv = gdb.string_to_argv(arg)

        if not argv:
            self.stdout(f'The current value is "{repr(self.option.value)}"')
            return

        self.option.value = argv[0]

    def complete(self, text, word):
        if isinstance(self.option.choices, int):
            return self.option.choices
        else:
            return complete(word, self.option.choices)
