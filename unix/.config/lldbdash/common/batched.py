import typing

TBatch = typing.TypeVar("TBatch")


def batched(iter: typing.Iterable[TBatch], n: int):
    batch: list[TBatch] = []
    for item in iter:
        batch.append(item)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch
