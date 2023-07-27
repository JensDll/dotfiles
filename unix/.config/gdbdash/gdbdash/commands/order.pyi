from typing import ClassVar, Protocol

from .command import CommandProtocol

class OrderableProtocol(CommandProtocol, Protocol):
    ORDER: ClassVar[int]

    def on_order_changed(self) -> None: ...

class Orderable:
    pass
