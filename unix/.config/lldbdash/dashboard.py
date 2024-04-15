import os

import lldb
import lldbdash.common
import lldbdash.modules


class Dashboard:
    modules: list[lldbdash.modules.Module]

    def __init__(
        self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, dict: dict
    ):
        pass

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream):
        size = os.terminal_size((160, 24))

        try:
            size = os.get_terminal_size(0)
        except OSError:
            stream.write("Failed to get terminal size\n")

        for module in Dashboard.modules:
            module.render(size, exe_ctx, stream)
