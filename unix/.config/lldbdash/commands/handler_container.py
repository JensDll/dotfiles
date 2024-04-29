import typing


class HandlerContainer:
    handle_count: typing.ClassVar[int] = 0
    handlers: list[str]

    def __init__(self, *handlers: typing.Callable):
        self.handlers = []
        for handler in handlers:
            handler_name = f"handle_{HandlerContainer.handle_count}"
            setattr(HandlerContainer, handler_name, handler)
            HandlerContainer.handle_count += 1
            self.handlers.append(
                f"{HandlerContainer.__module__}.{HandlerContainer.__name__}.{handler_name}"
            )
