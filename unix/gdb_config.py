import gdb  # pyright: ignore [reportMissingModuleSource]
import os
import sys


class Dashboard(gdb.Command):
    def __init__(self):
        super().__init__("dashboard", gdb.COMMAND_USER, gdb.COMPLETE_NONE, True)

        Dashboard.EnabledCommand(self)

        self.enabled = False

        gdb.events.stop.connect(self.on_stop)

    def invoke(self, arg, from_tty):
        super().dont_repeat()
        argv = gdb.string_to_argv(arg)
        print(argv)

    def on_stop(self, event: "gdb.events.StopEvent"):
        self.render()

    def render(self):
        print("render")
        pass

    class EnabledCommand(gdb.Command):
        def __init__(self, dashboard: "Dashboard"):
            super().__init__("dashboard enabled", gdb.COMMAND_USER)
            self.dashboard = dashboard

        def invoke(self, arg, from_tty):
            super().dont_repeat()
            argv = gdb.string_to_argv(arg)
            print(argv)


def get_terminal_size(fd=sys.stdout.fileno()):
    return os.get_terminal_size(fd)


def custom_prompt(current_prompt: str):
    # https://sourceware.org/gdb/current/onlinedocs/gdb.html/gdb_002eprompt.html#gdb_002eprompt
    prompt = gdb.prompt.substitute_prompt(r"\[\e[38;5;177m\]gdb\[\e[0m\]$ ")
    return prompt


gdb.prompt_hook = custom_prompt

Dashboard()
