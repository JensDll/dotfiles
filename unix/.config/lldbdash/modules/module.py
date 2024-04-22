import inspect
import os
import typing

import lldb
import lldbdash.commands
from lldbdash.common import Output


class Module(typing.Protocol):
    settings: dict[str, lldbdash.commands.Command]
    name: str
    enabled: lldbdash.commands.ToggleCommand

    @staticmethod
    def render(
        size: os.terminal_size, exe_ctx: lldb.SBExecutionContext, stream: Output
    ) -> None: ...


def is_module(obj: object) -> typing.TypeGuard[Module]:
    return (
        inspect.isclass(obj)
        and callable(getattr(obj, "render", None))
        and obj is not Module
    )
