import typing

T = typing.TypeVar("T")


def not_none(x: typing.Optional[T]) -> typing.TypeGuard[T]:
    return x is not None
