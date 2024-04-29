import lldb


def get_reg_set(frame: lldb.SBFrame, kind: str) -> lldb.SBValue:
    regs: lldb.SBValueList = frame.GetRegisters()

    for reg_set in regs:
        name: str = reg_set.GetName().lower()
        if kind in name:
            return reg_set

    raise ValueError(f"Register set '{kind}' not found")


def get_gp_reg_set(frame: lldb.SBFrame):
    return get_reg_set(frame, "general purpose")


def get_avx_reg_set(frame: lldb.SBFrame):
    return get_reg_set(frame, "advanced vector extensions")


def get_fp_reg_set(frame: lldb.SBFrame):
    return get_reg_set(frame, "floating point")
