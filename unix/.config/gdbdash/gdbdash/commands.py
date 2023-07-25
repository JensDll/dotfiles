import abc
import collections
import dataclasses
import typing

import gdb  # pyright: ignore [reportMissingModuleSource]
import gdbdash
import gdbdash.utils


class Command:
    def __init__(
        self,
        /,
        command_name: str,
        command_class: int,
        command_completer_class: typing.Optional[int] = None,
        command_prefix: bool = False,
        command_doc: typing.Optional[str] = None,
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
        print(f'The command "{self.command_name}" is not implemented')

    def complete(self, text, word):
        raise NotImplementedError


@dataclasses.dataclass
class BoolOption:
    doc: str
    value: gdbdash.utils.GdbBool = gdbdash.utils.GdbBool()
    choices: typing.Sequence[str] = gdbdash.utils.GdbBool.CHOICES


@dataclasses.dataclass
class IntOption:
    doc: str
    value: gdbdash.utils.GdbInt = gdbdash.utils.GdbInt()
    choices: int = gdb.COMPLETE_NONE


@dataclasses.dataclass
class StrOption:
    doc: str
    value: str
    choices: int = gdb.COMPLETE_NONE


Option = typing.Union[BoolOption, IntOption, StrOption]
Options = typing.Dict[str, Option]


class Configurable(metaclass=abc.ABCMeta):
    command_name: str

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "command_name"):
            raise TypeError("super() must initialize command_name instance variable")

        ConfigureCommand(self)

    @property
    @abc.abstractmethod
    def options(self) -> Options:
        pass


class ConfigureCommand(Command):
    def __init__(self, configurable: "Configurable"):
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
        print("TODO: options summary here")


class ConfigureOptionCommand(Command):
    def __init__(self, /, command_name: str, option_name: str, option: Option):
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
            print(
                f'The current value of option {self.option_name} is "{self.option.value}"'
            )
            return

        self.option.value = argv[0]

    def complete(self, text, word):
        if isinstance(self.option.choices, int):
            return self.option.choices
        else:
            return gdbdash.utils.complete(word, self.option.choices)


class Togglable:
    command_name: str

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "command_name"):
            raise TypeError("super() must initialize command_name instance variable")

        self.enabled = False
        self.enable()

        EnableCommand(self)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class EnableCommand(Command):
    gdb_bool = gdbdash.utils.GdbBool()

    def __init__(self, togglable: "Togglable"):
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
            print(
                f"[{self.togglable.command_name}] Is currently {self.togglable.enabled and 'enabled' or 'disabled'}"
            )
            return

        self.gdb_bool = argv[0]

        if self.gdb_bool:
            self.togglable.enable()
        else:
            self.togglable.disable()

    def complete(self, text, word):
        return gdbdash.utils.complete(word, gdbdash.utils.GdbBool.CHOICES)


class Outputable(metaclass=abc.ABCMeta):
    command_name: str

    def __init__(
        self, /, dashboard_modules: "gdbdash.DashboardModules", **kwargs
    ) -> None:
        super().__init__(**kwargs)

        if not hasattr(self, "command_name"):
            raise TypeError("super() must initialize command_name instance variable")

        self.dashboard_modules = dashboard_modules
        self.output: gdbdash.utils.FileDescriptorOrPath = gdb.STDOUT

        OutputCommand(self)

    def on_output_changed(self, old_output: gdbdash.utils.FileDescriptorOrPath):
        import gdbdash.modules

        if not isinstance(self, gdbdash.modules.Module):
            raise TypeError(f"{self} must be a {gdbdash.modules.Module}")

        deque = self.dashboard_modules[old_output]
        deque.remove(self)

        if len(deque) == 0:
            del self.dashboard_modules[old_output]

        self.dashboard_modules.setdefault(self.output, collections.deque()).append(self)


class OutputCommand(Command):
    def __init__(self, outputable: "Outputable"):
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

        if not argv:
            print(
                f'[{self.outputable.command_name}] The current output is "{self.outputable.output}"'
            )
            return

        old_output = self.outputable.output

        try:
            self.outputable.output = int(argv[0])
        except ValueError:
            self.outputable.output = argv[0]

        self.outputable.on_output_changed(old_output)
