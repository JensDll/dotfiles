from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.utils import complete

from .command import Command

if TYPE_CHECKING:
    from .configure import ConfigurableProtocol
    from .options import Option


class Configurable(metaclass=ABCMeta):
    def __init__(
        self,  # type: ConfigurableProtocol
        /,
        **kwargs,
    ):
        if not isinstance(self, Command):
            raise TypeError(f"{self} must be a {Command}")

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
