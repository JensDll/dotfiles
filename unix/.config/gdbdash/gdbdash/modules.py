from . import Dashboard


class Stack(Dashboard.Module):
    """Print stack information"""

    def label(self) -> str:
        return "stack"

    def render(self, terminal_size) -> None:
        pass


class Registers(Dashboard.Module):
    """Print register information"""

    def label(self) -> str:
        return "registers"

    def render(self, terminal_size) -> None:
        pass
