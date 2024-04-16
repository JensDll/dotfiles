import typing


def create_handlers(cls, *handlers: typing.Callable) -> list[str]:
    result = []

    for handler in handlers:
        handler_name = f"handle_{cls.handle_count}"
        setattr(cls, handler_name, handler)
        cls.handle_count += 1
        result.append(f"{cls.__module__}.{cls.__name__}.{handler_name}")

    return result
