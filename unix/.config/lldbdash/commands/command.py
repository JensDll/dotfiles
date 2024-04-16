import typing

from .create_handlers import create_handlers
from .show_command import ShowCommand

T = typing.TypeVar("T")

OnChange = typing.Callable[[T, T], None]


def default_on_change(prev_value: T, value: T):
    pass


class Command(typing.Generic[T]):
    handle_count = 0

    def __init__(
        self,
        initial_value: T,
        *handlers: typing.Callable,
        show_format: str,
        show_help: typing.Optional[str],
        show_long_help: typing.Optional[str],
        on_change: OnChange,
    ):
        self.value = initial_value
        self.on_change = on_change
        self.handlers = create_handlers(Command, *handlers)
        self.show_command = ShowCommand(self, show_format, show_help, show_long_help)

    def set_value(self, value: T):
        self.on_change(self.value, value)
        self.value = value
