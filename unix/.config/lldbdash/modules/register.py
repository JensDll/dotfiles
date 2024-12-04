import lldb


class GeneralPurposeRegister:
    def __init__(self, values: list[lldb.SBValue], prev_value: int):
        self.values = values
        self.value_int = values[0].GetValueAsSigned()
        self.value_uint = values[0].GetValueAsUnsigned()
        self.changed = self.value_uint != prev_value

    def get_name_64(self):
        return "'".join(value.GetName() for value in self.values)

    def get_hex_64(self) -> str:
        return "{:08x}'{:04x}'{:02x}'{:02x}".format(
            self.value_uint >> 32,
            (self.value_uint >> 16) & 0xFFFF,
            (self.value_uint >> 8) & 0xFF,
            self.value_uint & 0xFF,
        )


class SegmentRegister:
    def __init__(self, name: str, value: int, prev_value: int):
        self.name = name
        self.changed = value != prev_value
        self.hex_str = f"{value:04x}"


class RflagsRegister:
    def __init__(self, name: str, value: int, prev_value: int):
        self.name = name
        self.changed = value != prev_value
        # Control flags
        self.df = (value >> 10) & 1  # Direction flag
        self.df_changed = (prev_value >> 10) & 1 != self.df
        # System flags
        self.tf = (value >> 8) & 1  # Trap flag
        self.tf_changed = (prev_value >> 8) & 1 != self.tf
        self.if_ = (value >> 9) & 1  # Interrupt enable flag
        self.if_changed = (prev_value >> 9) & 1 != self.if_
        self.iopl = (value >> 12) & 3  # I/O privilege level
        self.iopl_changed = (prev_value >> 12) & 3 != self.iopl
        self.nt = (value >> 14) & 1  # Nested task flag
        self.nt_changed = (prev_value >> 14) & 1 != self.nt
        self.rf = (value >> 16) & 1  # Resume flag
        self.rf_changed = (prev_value >> 16) & 1 != self.rf
        self.vm = (value >> 17) & 1  # Virtual 8086 mode flag
        self.vm_changed = (prev_value >> 17) & 1 != self.vm
        self.ac = (value >> 18) & 1  # Alignment check / Access control flag
        self.ac_changed = (prev_value >> 18) & 1 != self.ac
        self.vif = (value >> 19) & 1  # Virtual interrupt flag
        self.vif_changed = (prev_value >> 19) & 1 != self.vif
        self.vip = (value >> 20) & 1  # Virtual interrupt pending flag
        self.vip_changed = (prev_value >> 20) & 1 != self.vip
        self.id = (value >> 21) & 1  # Identification flag
        self.id_changed = (prev_value >> 21) & 1 != self.id
        # Status flags
        self.cf = value & 1  # Carry flag
        self.cf_changed = prev_value & 1 != self.cf
        self.pf = (value >> 2) & 1  # Parity flag
        self.pf_changed = (prev_value >> 2) & 1 != self.pf
        self.af = (value >> 4) & 1  # Auxiliary carry flag
        self.af_changed = (prev_value >> 4) & 1 != self.af
        self.zf = (value >> 6) & 1  # Zero flag
        self.zf_changed = (prev_value >> 6) & 1 != self.zf
        self.sf = (value >> 7) & 1  # Sign flag
        self.sf_changed = (prev_value >> 7) & 1 != self.sf
        self.of = (value >> 11) & 1  # Overflow flag
        self.of_changed = (prev_value >> 11) & 1 != self.of


class MxcsrRegister:
    def __init__(self, name: str, value: int, prev_value: int):
        self.name = name
        self.changed = value != prev_value
        self.ie = value & 1  # Invalid operation flags
        self.ie_changed = prev_value & 1 != self.ie
        self.de = (value >> 1) & 1  # Denormal flag
        self.de_changed = (prev_value >> 1) & 1 != self.de
        self.ze = (value >> 2) & 1  # Divide-by-zero flag
        self.ze_changed = (prev_value >> 2) & 1 != self.ze
        self.oe = (value >> 3) & 1  # Overflow flag
        self.oe_changed = (prev_value >> 3) & 1 != self.oe
        self.ue = (value >> 4) & 1  # Underflow flag
        self.ue_changed = (prev_value >> 4) & 1 != self.ue
        self.pe = (value >> 5) & 1  # Precision flag
        self.pe_changed = (prev_value >> 5) & 1 != self.pe
        self.daz = (value >> 6) & 1  # Denormals are zero
        self.daz_changed = (prev_value >> 6) & 1 != self.daz
        self.im = (value >> 7) & 1  # Invalid operation mask
        self.im_changed = (prev_value >> 7) & 1 != self.im
        self.dm = (value >> 8) & 1  # Denormal mask
        self.dm_changed = (prev_value >> 8) & 1 != self.dm
        self.zm = (value >> 9) & 1  # Divide-by-zero mask
        self.zm_changed = (prev_value >> 9) & 1 != self.zm
        self.om = (value >> 10) & 1  # Overflow mask
        self.om_changed = (prev_value >> 10) & 1 != self.om
        self.um = (value >> 11) & 1  # Underflow mask
        self.um_changed = (prev_value >> 11) & 1 != self.um
        self.pm = (value >> 12) & 1  # Precision mask
        self.pm_changed = (prev_value >> 12) & 1 != self.pm
        self.rc = (value >> 13) & 3  # Rounding control
        self.rc_changed = (prev_value >> 13) & 3 != self.rc
        self.ftz = (value >> 15) & 1  # Flush to zero
        self.ftz_changed = (prev_value >> 15) & 1 != self.ftz


class AvxRegister:
    def __init__(
        self, name_ymm: str, name_xmm: str, values: list[int], prev_values: list[int]
    ):
        self.name_ymm = name_ymm
        self.name_xmm = name_xmm
        self.values = values
        self.changed_xmm: bool = any(prev_values[i] != values[i] for i in range(16))
        self.changed_ymm: bool = any(prev_values[i] != values[i] for i in range(16, 32))
