import gdb  # pyright: ignore [reportMissingModuleSource]


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

        if command_completer_class is None:
            self.command = cls(command_name, command_class, prefix=command_prefix)
        else:
            self.command = cls(
                command_name, command_class, command_completer_class, command_prefix
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
