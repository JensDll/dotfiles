import collections
import functools
import inspect
import itertools
import typing

import gdb  # pyright: ignore [reportMissingModuleSource]
import gdbdash.commands
import gdbdash.modules
import gdbdash.utils

DashboardOptions = typing.TypedDict(
    "DashboardOptions",
    {
        "text-highlight": gdbdash.commands.StrOption,
        "text-divider": gdbdash.commands.StrOption,
        "text-divider-title": gdbdash.commands.StrOption,
        "text-100": gdbdash.commands.StrOption,
        "text-200": gdbdash.commands.StrOption,
        "divider-fill-char": gdbdash.commands.StrOption,
    },
)

DashboardModules = typing.Dict[
    gdbdash.utils.FileDescriptorOrPath,
    "collections.deque[gdbdash.modules.Module]",
]


class Dashboard(
    gdbdash.commands.Command,
    gdbdash.commands.Togglable,
    gdbdash.commands.Configurable,
    gdbdash.commands.Outputable,
):
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
            if inspect.isclass(value)
            and issubclass(value, gdbdash.modules.Module)
            and value is not gdbdash.modules.Module
        ]

    @functools.cached_property
    def modules(self):
        result: DashboardModules = dict()

        for module_type in self.module_types:
            module = module_type(
                dashboard_options=self.options, dashboard_modules=result
            )
            result.setdefault(module.output, collections.deque()).append(module)

        return result

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        if argv:
            gdbdash.utils.write_err(f"Dashboard invalid argument: {argv[0]}\n")
        elif not gdbdash.utils.is_running():
            gdbdash.utils.write_err("The program is not running\n")
        else:
            self.render()

    def render(self):
        width = 160
        height = 24

        for output, modules in self.modules.items():
            if isinstance(output, int):
                try:
                    width, height = gdbdash.utils.get_terminal_size(output)
                except OSError as e:
                    print(
                        f"Failed to get terminal size using fallback values (width = {width}, height = {height}):",
                        e,
                    )

                write = functools.partial(gdb.write, stream=output)

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

    def on_stop_handler(self, event: "gdb.events.StopEvent"):
        if gdbdash.utils.is_running():
            self.render()

    def on_output_changed(self, old_output: gdbdash.utils.FileDescriptorOrPath):
        deque = collections.deque()
        modules = dict(((self.output, deque),))

        for module in itertools.chain.from_iterable(self.modules.values()):
            module.output = self.output
            module.dashboard_modules = modules
            deque.append(module)

        self.modules = modules

    @functools.cached_property
    def options(self) -> DashboardOptions:
        return {
            "text-highlight": gdbdash.commands.StrOption(
                "Text highlight color", "\033[1;38;5;40m"
            ),
            "text-divider": gdbdash.commands.StrOption(
                "Divider color", "\033[38:5:111m"
            ),
            "text-divider-title": gdbdash.commands.StrOption(
                "Divider title color", "\033[38:5:111m"
            ),
            "text-100": gdbdash.commands.StrOption(
                "Light text color", "\033[38:5:251m"
            ),
            "text-200": gdbdash.commands.StrOption(
                "Darker text color", "\033[38:5:245m"
            ),
            "divider-fill-char": gdbdash.commands.StrOption("Divider char", "─"),
        }


def custom_prompt(current_prompt: str):
    # https://sourceware.org/gdb/current/onlinedocs/gdb.html/gdb_002eprompt.html#gdb_002eprompt
    prompt = gdb.prompt.substitute_prompt(r"\[\e[38;5;177m\]gdb\[\e[0m\]$ ")
    return prompt


def start():
    gdb.prompt_hook = custom_prompt
    Dashboard()
