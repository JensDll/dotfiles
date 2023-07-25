import collections
import itertools
from functools import cached_property, partial
from inspect import isclass
from os import get_terminal_size
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
import gdbdash.modules

from .commands import Command, Configurable, Outputable, StrOption, Togglable
from .modules import Module
from .utils import is_running

if TYPE_CHECKING:
    from gdb.events import StopEvent  # pyright: ignore [reportMissingModuleSource]

    from . import DashboardModules


class Dashboard(Command, Togglable, Configurable, Outputable):
    def __init__(self):
        super().__init__(
            command_name="dashboard",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
            dashboard_modules=dict(),
        )

        self.module_types = [
            value
            for value in vars(gdbdash.modules).values()
            if isclass(value)
            and issubclass(value, Module)
            and value is not gdbdash.modules.Module
        ]

    @cached_property
    def modules(self):
        result = dict()  # type: DashboardModules

        for module_type in self.module_types:
            module = module_type(
                dashboard_options=self.options, dashboard_modules=result
            )
            result.setdefault(module.output, collections.deque()).append(module)

        return result

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        if len(argv) > 0:
            self.stderr(f"Invalid argument: {argv[0]}\n")
        elif not is_running():
            self.stderr("The program is not running\n")
        else:
            self.render()

    def render(self):
        width = 160
        height = 24

        for output, modules in self.modules.items():
            if isinstance(output, int):
                try:
                    width, height = get_terminal_size(output)
                except OSError as e:
                    self.stderr(
                        f"Failed to get terminal size using fallback values (width = {width}, height = {height}): {e}\n"
                    )

                write = partial(gdb.write, stream=output)

                for module in modules:
                    module.divider(width, height, write)
                    module.render(width, height, write)
            else:
                with open(output, "w") as f:
                    for module in modules:
                        module.divider(width, height, f.write)
                        module.render(width, height, f.write)

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

    def on_stop_handler(self, event):  # type: (StopEvent) -> None
        if is_running():
            self.render()

    def on_output_changed(self, old_output):
        deque = collections.deque()
        modules = dict(((self.output, deque),))  # type: DashboardModules

        for module in itertools.chain.from_iterable(self.modules.values()):
            module.output = self.output
            module.dashboard_modules = modules
            deque.append(module)

        self.modules = modules

    @cached_property
    def options(self):
        return {
            "text-highlight": StrOption("Text highlight color", "\033[1;38;5;40m"),
            "text-divider": StrOption("Divider color", "\033[38:5:111m"),
            "text-divider-title": StrOption("Divider title color", "\033[38:5:111m"),
            "text-100": StrOption("Text color", "\033[38:5:251m"),
            "text-200": StrOption("Text color", "\033[38:5:245m"),
            "divider-fill-char": StrOption(
                "Char used for the module divider line", "─"
            ),
        }


def custom_prompt(current_prompt):  # type: (str) -> str
    # https://sourceware.org/gdb/current/onlinedocs/gdb.html/gdb_002eprompt.html#gdb_002eprompt
    prompt = gdb.prompt.substitute_prompt(r"\[\e[38;5;177m\]gdb\[\e[0m\]$ ")
    return prompt


def start():
    gdb.prompt_hook = custom_prompt
    Dashboard()
