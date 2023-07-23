import os
import typing

import gdb  # pyright: ignore [reportMissingModuleSource]


def is_running():
    return gdb.selected_inferior().pid != 0


def write_err(msg: str):
    gdb.write(msg, gdb.STDERR)


def get_terminal_size(fd=gdb.STDOUT):
    return os.get_terminal_size(fd)


def complete(word: str, candidates: typing.Sequence[str]):
    return filter(lambda candidate: candidate.startswith(word), candidates)


class GdbBool:
    CHOICES: typing.Final = ("on", "1", "enable", "off", "0", "disable")

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return False

        if getattr(instance, self._name):
            return "on"
        else:
            return "off"

    def __set__(self, instance, value):
        setattr(instance, self._name, GdbBool.to_python(value))

    @staticmethod
    def to_python(value: str) -> bool:
        if value == "on" or value == "1" or value == "enable":
            return True
        elif value == "off" or value == "0" or value == "disable":
            return False
        else:
            raise ValueError(f"Invalid boolean value: {value}")


class GdbInt:
    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return False

        return getattr(instance, self._name)

    def __set__(self, instance, value):
        setattr(instance, self._name, int(value))
