import gdb  # pyright: ignore [reportMissingModuleSource]
import os
import importlib
import inspect


class Dashboard(gdb.Command):
    def __init__(self):
        super().__init__("dashboard", gdb.COMMAND_USER, gdb.COMPLETE_NONE, True)

        Dashboard.EnabledCommand(self)

        self.enabled = False
        self.modules: list[Dashboard.ModuleInfo] = []

        for value in importlib.import_module("gdbdash.modules").__dict__.values():
            if inspect.isclass(value) and issubclass(value, Dashboard.Module):
                self.modules.append(Dashboard.ModuleInfo(self, value))

        self.enable()

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        if argv:
            write_err(f"Invalid argument: {argv[0]}\n")
        elif not is_running():
            write_err(
                "The program is not running. Make sure `gdb` has stopped before running `dashboard`\n"
            )
        else:
            self.render()

    def render(self):
        print("render")

    def enable(self):
        if self.enabled:
            return
        self.enabled = True
        gdb.events.stop.connect(self.on_stop_handler)
        gdb.events.cont.connect(self.on_continue_handler)

    def disable(self):
        if not self.enabled:
            return
        self.enabled = False
        gdb.events.stop.disconnect(self.on_stop_handler)
        gdb.events.cont.disconnect(self.on_continue_handler)

    def on_stop_handler(self, event: "gdb.events.StopEvent"):
        if is_running():
            self.render()

    def on_continue_handler(self, event: "gdb.events.ContinueEvent"):
        pass

    class EnabledCommand(gdb.Command):
        def __init__(self, dashboard: "Dashboard"):
            super().__init__("dashboard -enabled", gdb.COMMAND_USER)
            self.dashboard = dashboard

        def invoke(self, arg, from_tty):
            super().dont_repeat()
            argv = gdb.string_to_argv(arg)
            if not argv:
                print(
                    f"The dashboard is currently {self.dashboard.enabled and 'enabled' or 'disabled'}"
                )
            elif argv[0] == "on":
                self.dashboard.enable()
            elif argv[0] == "off":
                self.dashboard.disable()
            else:
                write_err(f"Invalid argument: {argv[0]}; must be on or off\n")

        def complete(self, text, word):
            return ["on", "off"]

    class Module:
        def label(self) -> str:
            return ""

    class ModuleInfo:
        def __init__(self, dashboard: "Dashboard", module: type["Dashboard.Module"]):
            self.instance = module()


def get_terminal_size(fd=gdb.STDOUT):
    return os.get_terminal_size(fd)


def custom_prompt(current_prompt: str):
    # https://sourceware.org/gdb/current/onlinedocs/gdb.html/gdb_002eprompt.html#gdb_002eprompt
    prompt = gdb.prompt.substitute_prompt(r"\[\e[38;5;177m\]gdb\[\e[0m\]$ ")
    return prompt


def is_running():
    return gdb.selected_inferior().pid != 0


def write_err(msg: str):
    gdb.write(msg, gdb.STDERR)


def start():
    gdb.prompt_hook = custom_prompt
    Dashboard()
