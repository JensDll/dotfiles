import typing

from .handler_container import HandlerContainer
from .show_command import ShowCommand

T = typing.TypeVar("T")

OnChange = typing.Callable[[T, T], None]


def default_on_change(prev_value: T, value: T):
    pass


class Command(HandlerContainer, typing.Generic[T]):
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
        self.show_command = ShowCommand(self, show_format, show_help, show_long_help)
        super().__init__(*handlers)

    def set_value(self, value: T):
        self.on_change(self.value, value)
        self.value = value

    def __str__(self):
        return str(self.value)
