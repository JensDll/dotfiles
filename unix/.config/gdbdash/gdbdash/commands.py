import collections
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

import gdb  # pyright: ignore [reportMissingModuleSource]

from .utils import GdbBool, GdbInt, complete


@dataclass
class BoolOption:
    doc: str
    value: GdbBool = GdbBool()
    choices: Sequence[str] = GdbBool.CHOICES


@dataclass
class IntOption:
    doc: str
    value: GdbInt = GdbInt()
    choices: int = gdb.COMPLETE_NONE


@dataclass
class StrOption:
    doc: str
    value: str
    choices: int = gdb.COMPLETE_NONE


class Command:
    def __init__(
        self,
        /,
        command_name,
        command_class,
        command_completer_class=None,
        command_prefix=False,
        command_doc=None,
        **kwargs,
    ):
        cls = type(
            "",
            (gdb.Command,),
            {
                "invoke": self.invoke,
                "complete": self.complete,
                "__doc__": command_doc or "(no documentation)",
            },
        )

        self.command = (
            cls(command_name, command_class, prefix=command_prefix)
            if command_completer_class is None
            else cls(
                command_name, command_class, command_completer_class, command_prefix
            )
        )

        self.command_name = command_name

        super().__init__(**kwargs)

    def dont_repeat(self):
        self.command.dont_repeat()

    def invoke(self, arg, from_tty):
        self.stdout(f"The command is not implemented")

    def complete(self, text, word):
        raise NotImplementedError

    def write(self, message, fd):
        gdb.write(f"[{self.command_name}] {message}\n", fd)

    def stdout(self, message):
        self.write(message, gdb.STDOUT)

    def stderr(self, message):
        self.write(message, gdb.STDERR)


class Configurable(metaclass=ABCMeta):
    def __init__(self, /, **kwargs):
        if not isinstance(self, Command):
            raise TypeError(f"{self} must be a {Command}")

        super().__init__(**kwargs)

        ConfigureCommand(self)

    @property
    @abstractmethod
    def options(self):
        pass


class ConfigureCommand(Command):
    def __init__(self, configurable):
        super().__init__(
            command_name=f"{configurable.command_name} -configure",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
        )

        for option_name, option in configurable.options.items():
            ConfigureOptionCommand(
                command_name=f"{self.command_name} {option_name}",
                option_name=option_name,
                option=option,
            )

    def invoke(self, arg, from_tty):
        self.stdout("TODO: options summary here")


class ConfigureOptionCommand(Command):
    def __init__(self, /, command_name, option_name, option):
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
            self.stdout(f'The current value is "{self.option.value}"')
            return

        self.option.value = argv[0]

    def complete(self, text, word):
        if isinstance(self.option.choices, int):
            return self.option.choices
        else:
            return complete(word, self.option.choices)


class Togglable:
    def __init__(self, /, **kwargs):
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
    gdb_bool = GdbBool()

    def __init__(self, togglable):
        super().__init__(
            command_name=f"{togglable.command_name} -enable",
            command_class=gdb.COMMAND_USER,
            command_prefix=False,
        )

        self.togglable = togglable

    def invoke(self, arg, from_tty):
        super().dont_repeat()
        argv = gdb.string_to_argv(arg)

        if not argv:
            self.togglable.stdout(
                f"Is currently {self.togglable.enabled and 'enabled' or 'disabled'}"
            )
            return

        self.gdb_bool = argv[0]

        if self.gdb_bool:
            self.togglable.enable()
        else:
            self.togglable.disable()

    def complete(self, text, word):
        return complete(word, GdbBool.CHOICES)


class Outputable:
    def __init__(self, /, dashboard_modules, **kwargs):
        if not isinstance(self, Command):
            raise TypeError(f"{self} must be a {Command}")

        super().__init__(**kwargs)

        self.dashboard_modules = dashboard_modules
        self.output = gdb.STDOUT

        OutputCommand(self)

    def on_output_changed(self, old_output):
        import gdbdash.modules

        if not isinstance(self, gdbdash.modules.Module):
            raise TypeError(f"{self} must be a {gdbdash.modules.Module}")

        deque = self.dashboard_modules[old_output]
        deque.remove(self)

        if len(deque) == 0:
            del self.dashboard_modules[old_output]

        self.dashboard_modules.setdefault(self.output, collections.deque()).append(self)


class OutputCommand(Command):
    def __init__(self, outputable):
        super().__init__(
            command_name=f"{outputable.command_name} -output",
            command_class=gdb.COMMAND_USER,
            command_completer_class=gdb.COMPLETE_FILENAME,
            command_prefix=False,
        )

        self.outputable = outputable

    def invoke(self, arg, from_tty):
        super().dont_repeat()
        argv = gdb.string_to_argv(arg)

        if len(argv) == 0:
            self.stdout(f'The current output is "{self.outputable.output}"')
            return

        old_output = self.outputable.output

        try:
            self.outputable.output = int(argv[0])
        except ValueError:
            self.outputable.output = argv[0]

        self.outputable.on_output_changed(old_output)
