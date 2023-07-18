from . import Dashboard


class Stack(Dashboard.Module):
    def label(self) -> str:
        return Stack.__name__


class Registers(Dashboard.Module):
    def label(self) -> str:
        return Registers.__name__
