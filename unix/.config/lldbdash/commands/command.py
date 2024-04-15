import typing

T = typing.TypeVar("T")


class Command(typing.Generic[T]):
    handle_count = 0

    def __init__(self, value: T, *handlers: typing.Callable):
        self.value = value
        self.prev_value = value
        self.handlers = create_handlers(Command, *handlers)

    def set_value(self, value: T):
        self.prev_value = self.value
        self.value = value


class EmptyCommand:
    handle_count = 0

    def __init__(self, *handlers: typing.Callable):
        self.handlers = create_handlers(EmptyCommand, *handlers)


def create_handlers(cls, *handlers: typing.Callable) -> list[str]:
    result = []

    for handler in handlers:
        handler_name = f"handle_{cls.handle_count}"
        setattr(cls, handler_name, handler)
        cls.handle_count += 1
        result.append(f"{cls.__module__}.{cls.__name__}.{handler_name}")

    return result
