import shutil

import lldb
import lldbdash.modules

from .common import file_streams


class Dashboard:
    modules: list[lldbdash.modules.Module]

    def __init__(
        self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, dict: dict
    ):
        pass

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream):
        size = shutil.get_terminal_size((160, 24))
        for module in Dashboard.modules:
            module.render(
                size,
                exe_ctx,
                (
                    stream
                    if module.output.value == "0"
                    else file_streams[module.output.value]["stream"]
                ),
            )
