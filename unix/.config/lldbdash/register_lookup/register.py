import lldb


class GeneralPurposeRegister:
    def __init__(self, values: list[lldb.SBValue], prev_value: int):
        self.name: str = "'".join([value.GetName() for value in values])
        self.value_int: int = values[0].GetValueAsSigned()
        self.value_uint: int = values[0].GetValueAsUnsigned()
        self.changed: bool = prev_value != self.value_uint
        self.hex_str: str = "{:08x}'{:04x}'{:02x}'{:02x}".format(
            self.value_uint >> 32,
            (self.value_uint >> 16) & 0xFFFF,
            (self.value_uint >> 8) & 0xFF,
            self.value_uint & 0xFF,
        )


class SegmentRegister:
    def __init__(self, value: lldb.SBValue, prev_value: int):
        self.name: str = value.GetName()
        self.value_int: int = value.GetValueAsSigned()
        self.value_uint: int = value.GetValueAsUnsigned()
        self.changed: bool = prev_value != self.value_uint
        self.hex_str: str = f"{self.value_uint:04x}"


class RflagsRegister:
    def __init__(self, value: lldb.SBValue, prev_value: int):
        self.name: str = value.GetName()
        self.value_int: int = value.GetValueAsSigned()
        self.value_uint: int = value.GetValueAsUnsigned()
        self.changed: bool = prev_value != self.value_uint
        # Control flags
        self.df = (self.value_uint >> 10) & 1  # Direction flag
        self.df_changed = (prev_value >> 10) & 1 != self.df
        # System flags
        self.tf = (self.value_uint >> 8) & 1  # Trap flag
        self.tf_changed = (prev_value >> 8) & 1 != self.tf
        self.if_ = (self.value_uint >> 9) & 1  # Interrupt enable flag
        self.if_changed = (prev_value >> 9) & 1 != self.if_
        self.iopl = (self.value_uint >> 12) & 3  # I/O privilege level
        self.iopl_changed = (prev_value >> 12) & 3 != self.iopl
        self.nt = (self.value_uint >> 14) & 1  # Nested task flag
        self.nt_changed = (prev_value >> 14) & 1 != self.nt
        self.rf = (self.value_uint >> 16) & 1  # Resume flag
        self.rf_changed = (prev_value >> 16) & 1 != self.rf
        self.vm = (self.value_uint >> 17) & 1  # Virtual 8086 mode flag
        self.vm_changed = (prev_value >> 17) & 1 != self.vm
        self.ac = (self.value_uint >> 18) & 1  # Alignment check / Access control flag
        self.ac_changed = (prev_value >> 18) & 1 != self.ac
        self.vif = (self.value_uint >> 19) & 1  # Virtual interrupt flag
        self.vif_changed = (prev_value >> 19) & 1 != self.vif
        self.vip = (self.value_uint >> 20) & 1  # Virtual interrupt pending flag
        self.vip_changed = (prev_value >> 20) & 1 != self.vip
        self.id = (self.value_uint >> 21) & 1  # Identification flag
        self.id_changed = (prev_value >> 21) & 1 != self.id
        # Status flags
        self.cf = self.value_uint & 1  # Carry flag
        self.cf_changed = prev_value & 1 != self.cf
        self.pf = (self.value_uint >> 2) & 1  # Parity flag
        self.pf_changed = (prev_value >> 2) & 1 != self.pf
        self.af = (self.value_uint >> 4) & 1  # Auxiliary carry flag
        self.af_changed = (prev_value >> 4) & 1 != self.af
        self.zf = (self.value_uint >> 6) & 1  # Zero flag
        self.zf_changed = (prev_value >> 6) & 1 != self.zf
        self.sf = (self.value_uint >> 7) & 1  # Sign flag
        self.sf_changed = (prev_value >> 7) & 1 != self.sf
        self.of = (self.value_uint >> 11) & 1  # Overflow flag
        self.of_changed = (prev_value >> 11) & 1 != self.of


class MxcsrRegister:
    def __init__(self, value: lldb.SBValue, prev_value: int):
        self.name: str = value.GetName()
        self.value_int: int = value.GetValueAsSigned()
        self.value_uint: int = value.GetValueAsUnsigned()
        self.changed: bool = prev_value != self.value_uint
        self.ie = self.value_uint & 1  # Invalid operation flags
        self.ie_changed = prev_value & 1 != self.ie
        self.de = (self.value_uint >> 1) & 1  # Denormal flag
        self.de_changed = (prev_value >> 1) & 1 != self.de
        self.ze = (self.value_uint >> 2) & 1  # Divide-by-zero flag
        self.ze_changed = (prev_value >> 2) & 1 != self.ze
        self.oe = (self.value_uint >> 3) & 1  # Overflow flag
        self.oe_changed = (prev_value >> 3) & 1 != self.oe
        self.ue = (self.value_uint >> 4) & 1  # Underflow flag
        self.ue_changed = (prev_value >> 4) & 1 != self.ue
        self.pe = (self.value_uint >> 5) & 1  # Precision flag
        self.pe_changed = (prev_value >> 5) & 1 != self.pe
        self.daz = (self.value_uint >> 6) & 1  # Denormals are zero
        self.daz_changed = (prev_value >> 6) & 1 != self.daz
        self.im = (self.value_uint >> 7) & 1  # Invalid operation mask
        self.im_changed = (prev_value >> 7) & 1 != self.im
        self.dm = (self.value_uint >> 8) & 1  # Denormal mask
        self.dm_changed = (prev_value >> 8) & 1 != self.dm
        self.zm = (self.value_uint >> 9) & 1  # Divide-by-zero mask
        self.zm_changed = (prev_value >> 9) & 1 != self.zm
        self.om = (self.value_uint >> 10) & 1  # Overflow mask
        self.om_changed = (prev_value >> 10) & 1 != self.om
        self.um = (self.value_uint >> 11) & 1  # Underflow mask
        self.um_changed = (prev_value >> 11) & 1 != self.um
        self.pm = (self.value_uint >> 12) & 1  # Precision mask
        self.pm_changed = (prev_value >> 12) & 1 != self.pm
        self.rc = (self.value_uint >> 13) & 3  # Rounding control
        self.rc_changed = (prev_value >> 13) & 3 != self.rc
        self.ftz = (self.value_uint >> 15) & 1  # Flush to zero
        self.ftz_changed = (prev_value >> 15) & 1 != self.ftz


class AvxRegister:
    def __init__(self, ymm: lldb.SBValue, xmm: lldb.SBValue, prev_values: list[int]):
        self.name_ymm: str = ymm.GetName()
        self.name_xmm: str = xmm.GetName()
        self.values: list[int] = [child.GetValueAsUnsigned() for child in ymm]
        self.changed_xmm: bool = any(
            prev_values[i] != self.values[i] for i in range(16)
        )
        self.changed_ymm: bool = any(
            prev_values[i] != self.values[i] for i in range(16, 32)
        )
