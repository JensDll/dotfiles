import functools
import inspect
import typing

import gdb  # pyright: ignore [reportMissingModuleSource]
import gdbdash.commands
import gdbdash.modules
import gdbdash.utils


class Dashboard(gdbdash.commands.Command, gdbdash.commands.Togglable):
    def __init__(self):
        super().__init__(
            command_name="dashboard",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
        )

    @functools.cached_property
    def modules(self) -> typing.Sequence[gdbdash.modules.Module]:
        return [
            module()
            for module in vars(gdbdash.modules).values()
            if inspect.isclass(module)
            and issubclass(module, gdbdash.modules.Module)
            and module is not gdbdash.modules.Module
        ]

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        if argv:
            gdbdash.utils.write_err(f"Dashboard invalid argument: {argv[0]}\n")
        elif not gdbdash.utils.is_running():
            gdbdash.utils.write_err("The program is not running")
        else:
            self.render()

    def render(self):
        super().dont_repeat()
        for module in self.modules:
            width, hight = gdbdash.utils.get_terminal_size(module.output)
            module.render(width, hight)

    def enable(self):
        if self.enabled:
            return
        super().enable()
        gdb.events.stop.connect(self.on_stop_handler)

    def disable(self):
        if not self.enabled:
            return
        super().disable()
        gdb.events.stop.disconnect(self.on_stop_handler)

    def on_stop_handler(self, event: "gdb.events.StopEvent"):
        if gdbdash.utils.is_running():
            self.render()


def custom_prompt(current_prompt: str):
    # https://sourceware.org/gdb/current/onlinedocs/gdb.html/gdb_002eprompt.html#gdb_002eprompt
    prompt = gdb.prompt.substitute_prompt(r"\[\e[38;5;177m\]gdb\[\e[0m\]$ ")
    return prompt


def start():
    gdb.prompt_hook = custom_prompt
    Dashboard()
