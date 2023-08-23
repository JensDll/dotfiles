import itertools
import json
import pathlib
from functools import cached_property, partial
from inspect import isclass
from os import get_terminal_size
from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
import gdbdash.modules
import gdbdash.utils
from gdbdash.commands import (
    BoolOption,
    Command,
    Configurable,
    Dumpable,
    Outputable,
    StrOption,
    Togglable,
)

if TYPE_CHECKING:
    from typing import Iterator

    from gdb.events import StopEvent  # pyright: ignore [reportMissingModuleSource]
    from gdbdash.utils import FileDescriptorOrPath

    from .dashboard import DashboardModulesDict, DashboardOptions


class Dashboard(Command, Togglable, Configurable, Outputable, Dumpable):
    def __init__(self):
        super().__init__(
            command_name="dashboard",
            command_class=gdb.COMMAND_USER,
            command_prefix=True,
        )

        self.config_path = pathlib.Path.cwd() / "gdbdash.json"
        self.config_modified_time = 0

        self.module_types = [
            value
            for value in vars(gdbdash.modules).values()
            if isclass(value)
            and issubclass(value, gdbdash.modules.Module)
            and value is not gdbdash.modules.Module
        ]

        gdb.events.stop.connect(self.on_stop_handler)

    @cached_property
    def modules_dict(self):
        modules_dict = dict()  # type: DashboardModulesDict

        for module_type in self.module_types:
            module = module_type(options=self.options, outputables=modules_dict)
            modules_dict.setdefault(module.output, []).append(module)

        for modules in modules_dict.values():
            modules.sort(key=lambda module: module.ORDER)

        return modules_dict

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)

        if len(argv) > 0:
            self.stderr(f"Invalid argument: {argv[0]}")
        elif not is_running():
            self.stderr("The program is not running")
        else:
            self.render()

    def render(self):
        self.try_load_config()

        if not self.enabled:
            return

        width = 160
        height = 24

        def render_file(
            output, modules
        ):  # type: (FileDescriptorOrPath, Iterator[gdbdash.modules.Module]) -> None
            next_module = next(modules, None)

            if next_module is None:
                return

            with open(output, "w") as f:
                next_module.divider(width, height, f.write)
                next_module.render(width, height, f.write)
                for module in modules:
                    module.divider(width, height, f.write)
                    module.render(width, height, f.write)

        for output, modules in self.modules_dict.items():
            modules = filter(lambda module: module.enabled, modules)

            if not isinstance(output, int):
                render_file(output, modules)
                continue

            try:
                width, height = get_terminal_size(output)
            except OSError:
                if output:
                    # File descriptor is not a terminal, try rendering to file
                    render_file(output, modules)
                continue

            write = partial(gdb.write, stream=output)

            for module in modules:
                module.divider(width, height, write)
                module.render(width, height, write)

    def on_stop_handler(self, event):  # type: (StopEvent) -> None
        self.render()

    def on_output_changed(self, old_output):
        modules = []  # type: list[gdbdash.modules.Module]
        modules_dict = dict(((self.output, modules),))  # type: DashboardModulesDict

        for module in itertools.chain.from_iterable(self.modules_dict.values()):
            module.output = self.output
            module.outputables = modules_dict
            modules.append(module)

        modules.sort(key=lambda module: module.ORDER)

        self.modules_dict = modules_dict

    def dump(self, path):
        values = {
            "dashboard": {
                "enabled": self.enabled,
                "options": {
                    option_name: option.value  # type: ignore
                    for option_name, option in self.options.items()
                },
            }
        }

        values["dashboard"]["modules"] = {
            module.normalized_name: {
                "enabled": module.enabled,
                "options": {
                    option_name: option.value
                    for option_name, option in module.options.items()
                },
            }
            for module in itertools.chain.from_iterable(self.modules_dict.values())
        }

        with open(path, "w") as f:
            json.dump(values, f, indent=2)

    def load(self, path):
        with open(path) as f:
            config = json.load(f)

        json_dashboard = config["dashboard"]
        self.enabled = json_dashboard["enabled"]
        for option_name, option in json_dashboard["options"].items():
            self.options[option_name].value = option

        for module in itertools.chain.from_iterable(self.modules_dict.values()):
            json_module = config["dashboard"]["modules"][module.normalized_name]
            module.enabled = json_module["enabled"]
            for option_name, option in json_module["options"].items():
                module.options[option_name].value = option

    def try_load_config(self):
        if self.config_path.is_file():
            config_modified_time = self.config_path.stat().st_mtime
            if config_modified_time > self.config_modified_time:
                self.config_modified_time = config_modified_time
                self.load(self.config_path)

    @cached_property
    def options(self):  # type: () -> DashboardOptions
        return {
            "text-highlight": StrOption("", "\033[1;38;5;220m"),
            "text-secondary": StrOption("", "\033[0;38;5;245m"),
            "text-divider": StrOption("", "\033[38;5;240m"),
            "text-divider-title": StrOption("", "\033[1;38;5;245m"),
            "divider-fill-char": StrOption("", "─"),
            "show-divider": BoolOption("", "on"),
        }


def is_running():
    return gdb.selected_inferior().pid != 0
