from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]

from .command import Command

if TYPE_CHECKING:
    from .output import OutputableProtocol


class Outputable:
    def __init__(
        self,  # type: OutputableProtocol
        /,
        **kwargs,
    ):
        if not isinstance(self, Command):
            raise TypeError(f"{self} must be a {Command}")

        super().__init__(**kwargs)

        self.output = gdb.STDOUT

        OutputCommand(self)

    def on_output_changed(self, old_output):
        import gdbdash.modules

        if not isinstance(self, gdbdash.modules.Module):
            raise TypeError(f"{self} must be a {gdbdash.modules.Module}")

        modules = self.outputables[old_output]
        modules.remove(self)

        if len(modules) == 0:
            del self.outputables[old_output]

        modules = self.outputables.setdefault(self.output, [])
        modules.append(self)
        modules.sort(key=lambda module: module.ORDER)


class OutputCommand(Command):
    def __init__(
        self,
        outputable,  # type: OutputableProtocol
    ):
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
