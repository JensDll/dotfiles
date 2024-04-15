import inspect
import os
import typing

import lldb
import lldbdash.commands
import lldbdash.common


class Module(typing.Protocol):
    settings: dict[str, lldbdash.commands.Command]
    name: str
    output: lldbdash.commands.StrCommand
    enabled: lldbdash.commands.ToggleCommand

    @staticmethod
    def render(
        size: os.terminal_size, exe_ctx: lldb.SBExecutionContext, stream: lldb.SBStream
    ) -> None: ...


def is_module(obj: object) -> typing.TypeGuard[Module]:
    return (
        inspect.isclass(obj)
        and callable(getattr(obj, "render", None))
        and obj is not Module
    )
