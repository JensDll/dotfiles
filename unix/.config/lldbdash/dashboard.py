import shutil
import typing

import lldb
import lldbdash.modules

from .common import file_streams


class Dashboard:
    modules: typing.ClassVar[list[lldbdash.modules.Module]]

    def __init__(
        self, target: lldb.SBTarget, extra_args: lldb.SBStructuredData, dict: dict
    ):
        self.size = shutil.get_terminal_size((160, 24))

    def handle_stop(self, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream):
        for module in Dashboard.modules:
            module.render(
                self.size,
                exe_ctx,
                (
                    stream
                    if module.output.value == "0"
                    else file_streams[module.output.value]["stream"]
                ),
            )
