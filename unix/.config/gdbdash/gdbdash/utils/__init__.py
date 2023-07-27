RESET_COLOR = "\033[0m"
FONT_BOLD = "\033[1m"


def complete(word, candidates):
    return filter(lambda candidate: candidate.startswith(word), candidates)


class GdbBool:
    CHOICES = ("on", "1", "enable", "off", "0", "disable")

    def __init__(self, default=False):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self._default

        return getattr(instance, self._name, self._default)

    def __set__(self, instance, value):
        setattr(instance, self._name, GdbBool.to_python(value))

    @staticmethod
    def to_python(value: str):
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
        return getattr(instance, self._name)

    def __set__(self, instance, value):
        setattr(instance, self._name, int(value))


def fetch_instructions(architecture, start_pc, count=1):
    return architecture.disassemble(start_pc, count=count)


def fetch_instructions_range(architecture, start_pc, end_pc):
    return architecture.disassemble(start_pc, end_pc=end_pc)


def fetch_pc(frame):
    return frame.pc()
