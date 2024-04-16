import typing

from .create_handlers import create_handlers


class PureCommand:
    handle_count = 0

    def __init__(self, *handlers: typing.Callable):
        self.handlers = create_handlers(PureCommand, *handlers)
