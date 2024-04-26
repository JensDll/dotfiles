import lldb


def get_register_set(frame: lldb.SBFrame, kind: str) -> lldb.SBValue:
    registers: lldb.SBValueList = frame.GetRegisters()

    for reg_set in registers:
        reg_set_name: str = reg_set.GetName().lower()
        if kind in reg_set_name:
            return reg_set

    raise ValueError(f"Register set '{kind}' not found")


def get_gp_register_set(frame: lldb.SBFrame):
    return get_register_set(frame, "general purpose")
