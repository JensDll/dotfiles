import typing

from .handler_container import HandlerContainer


class PureCommand(HandlerContainer):
    def __init__(self, *handlers: typing.Callable):
        super().__init__(*handlers)
