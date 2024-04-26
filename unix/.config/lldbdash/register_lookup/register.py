import lldb


class Register:
    def __init__(self, values: list[lldb.SBValue], prev_value: int):
        self.name = "'".join([value.GetName() for value in values])

        self.int = values[0].GetValueAsSigned()
        self.uint = values[0].GetValueAsUnsigned()

        self.hex_str = "{:08x}'{:04x}'{:02x}'{:02x}".format(
            self.uint >> 32,
            (self.uint >> 16) & 0xFFFF,
            (self.uint >> 8) & 0xFF,
            self.uint & 0xFF,
        )

        self.changed = prev_value != values[0].GetValueAsSigned()
