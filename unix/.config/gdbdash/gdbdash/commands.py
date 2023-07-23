import abc
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
        command_doc: str = "(no documentation)",
        **kwargs,
    ):
        cls = type(
            "",
            (gdb.Command,),
            {"invoke": self.invoke, "complete": self.complete, "__doc__": command_doc},
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


Option = typing.Union[BoolOption, IntOption]
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

        EnableCommand(self)
        self.enabled = False
        self.enable()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class EnableCommand(Command):
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
        elif argv[0] == "on":
            self.togglable.enable()
        elif argv[0] == "off":
            self.togglable.disable()
        else:
            gdbdash.utils.write_err(
                f"[{self.togglable.command_name}] Invalid argument: {argv[0]}; must be: on off\n"
            )

    def complete(self, text, word):
        return gdbdash.utils.complete(word, ("on", "off"))
