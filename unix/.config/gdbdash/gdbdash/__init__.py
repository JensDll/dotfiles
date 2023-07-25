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
    from typing import Sequence

    from gdb.events import StopEvent  # pyright: ignore [reportMissingModuleSource]

    from . import DashboardModulesDict, DashboardOptions
    from .utils import FileDescriptorOrPath


class Dashboard(Command, Togglable, Configurable, Outputable):
    def __init__(self):
        super().__init__(
            command_name="dashboard",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
            dashboard_modules_dict=dict(),
        )

        self.module_types = [
            value
            for value in vars(gdbdash.modules).values()
            if isclass(value)
            and issubclass(value, Module)
            and value is not gdbdash.modules.Module
        ]

    @cached_property
    def modules_dict(self):
        modules_dict = dict()  # type: DashboardModulesDict

        for module_type in self.module_types:
            module = module_type(
                dashboard_options=self.options, dashboard_modules_dict=modules_dict
            )
            modules_dict.setdefault(module.output, []).append(module)

        for modules in modules_dict.values():
            modules.sort(key=lambda module: module.ORDER)

        return modules_dict

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

        def render_file(
            output, modules
        ):  # type: (FileDescriptorOrPath, Sequence[Module]) -> None
            with open(output, "w") as f:
                for module in modules:
                    module.divider(width, height, f.write)
                    module.render(width, height, f.write)

        for output, modules in self.modules_dict.items():
            if not isinstance(output, int):
                render_file(output, modules)
                continue

            try:
                width, height = get_terminal_size(output)
            except OSError:
                # File descriptor is not a terminal, try rendering to file
                render_file(output, modules)
                continue

            write = partial(gdb.write, stream=output)

            for module in modules:
                module.divider(width, height, write)
                module.render(width, height, write)

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
        modules = []  # type: list[Module]
        modules_dict = dict(((self.output, modules),))  # type: DashboardModulesDict

        for module in itertools.chain.from_iterable(self.modules_dict.values()):
            module.output = self.output
            module.dashboard_modules_dict = modules_dict
            modules.append(module)

        modules.sort(key=lambda module: module.ORDER)

        self.modules_dict = modules_dict

    @cached_property
    def options(self):  # type: () -> DashboardOptions
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
