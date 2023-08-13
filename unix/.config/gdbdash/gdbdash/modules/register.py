from typing import TYPE_CHECKING

import gdb  # pyright: ignore [reportMissingModuleSource]
from gdbdash.utils import FONT_UNDERLINE, RESET_COLOR

if TYPE_CHECKING:
    from gdb import (  # pyright: ignore [reportMissingModuleSource]
        RegisterDescriptor,
        Type,
    )
    from gdbdash.dashboard import DashboardOptions


class Register:
    def __init__(
        self,
        descriptor,  # type: RegisterDescriptor
        int_type,  # type: Type
        options,  # type: DashboardOptions
    ):
        self.descriptor = descriptor
        self.name = descriptor.name
        self.int_type = int_type
        self.options = options


class GeneralPurposeRegister(Register):
    MAP32 = {
        "rax": "eax",
        "rbx": "ebx",
        "rcx": "ecx",
        "rdx": "edx",
        "rsi": "esi",
        "rdi": "edi",
        "rbp": "ebp",
        "rsp": "esp",
        "r8": "r8d",
        "r9": "r9d",
        "r10": "r10d",
        "r11": "r11d",
        "r12": "r12d",
        "r13": "r13d",
        "r14": "r14d",
        "r15": "r15d",
    }

    MAP16 = {
        "eax": "ax",
        "ebx": "bx",
        "ecx": "cx",
        "edx": "dx",
        "esi": "si",
        "edi": "di",
        "ebp": "bp",
        "esp": "sp",
        "r8d": "r8w",
        "r9d": "r9w",
        "r10d": "r10w",
        "r11d": "r11w",
        "r12d": "r12w",
        "r13d": "r13w",
        "r14d": "r14w",
        "r15d": "r15w",
    }

    MAP8H = {
        "ax": "ah",
        "bx": "bh",
        "cx": "ch",
        "dx": "dh",
    }

    MAP8L = {
        "ax": "al",
        "bx": "bl",
        "cx": "cl",
        "dx": "dl",
        "si": "sil",
        "di": "dil",
        "bp": "bpl",
        "sp": "spl",
        "r8w": "r8b",
        "r9w": "r9b",
        "r10w": "r10b",
        "r11w": "r11b",
        "r12w": "r12b",
        "r13w": "r13b",
        "r14w": "r14b",
        "r15w": "r15b",
    }

    def __init__(
        self,
        descriptor,  # type: RegisterDescriptor
        int_type,  # type: Type
        options,  # type: DashboardOptions
    ):
        super().__init__(descriptor, int_type, options)

        self.name32 = GeneralPurposeRegister.MAP32[self.name]
        self.name16 = GeneralPurposeRegister.MAP16[self.name32]
        self.name8h = GeneralPurposeRegister.MAP8H.get(self.name16)
        self.name8l = GeneralPurposeRegister.MAP8L[self.name16]

    def get_value(self, frame):  # type: (gdb.Frame) -> str
        self.value = frame.read_register(self.descriptor)
        value = self.value.cast(self.int_type)

        value64 = int(value)

        if getattr(self, "value64", value64) != value64:
            self.color = self.options["text-highlight"]
        else:
            self.color = self.options["text-secondary"]

        self.value64 = value64
        self.value32 = int(value & 0xFFFF_FFFF)

        return f"{self.color}{self.name:<4}{RESET_COLOR} {value64:#018x}  "

    def get_value_32(self):  # type: () -> str
        return (
            f"{self.color}{self.name32:<4}{RESET_COLOR}           {self.value32:08x}  "
        )

    def get_value_decimal(self):  # type: () -> str
        return (
            f"{self.color}={RESET_COLOR} {self.value.format_string(format='d'):>21}  "
        )


class SegmentRegister(Register):
    def get_value(self, frame):  # type: (gdb.Frame) -> str
        value = int(frame.read_register(self.descriptor))

        if getattr(self, "value", value) != value:
            color = self.options["text-highlight"]
        else:
            color = self.options["text-secondary"]

        self.value = value

        return f"{color}{self.name:>2}{RESET_COLOR} {value:#06x}  "


class FlagsRegister(Register):
    def flag(self, name, value):
        if value:
            return f"{FONT_UNDERLINE}{name}{RESET_COLOR}"
        else:
            return f"{self.options['text-secondary']}{name}{RESET_COLOR}"


class EflagsRegister(FlagsRegister):
    def get_value(self, frame):  # type: (gdb.Frame) -> str
        value = int(frame.read_register(self.descriptor))

        any_change = False

        # Control flags
        df = (value >> 10) & 1  # Direction flag
        any_change |= getattr(self, "df", df) != df
        self.df = df

        # System flags
        tf = (value >> 8) & 1  # Trap flag
        any_change |= getattr(self, "tf", tf) != tf
        self.tf = tf

        _if = (value >> 9) & 1  # Interrupt enable flag
        any_change |= getattr(self, "_if", _if) != _if
        self._if = _if

        iopl = (value >> 12) & 3  # I/O privilege level
        any_change |= getattr(self, "iopl", iopl) != iopl
        self.iopl = iopl

        nt = (value >> 14) & 1  # Nested task flag
        any_change |= getattr(self, "nt", nt) != nt
        self.nt = nt

        rf = (value >> 16) & 1  # Resume flag
        any_change |= getattr(self, "rf", rf) != rf
        self.rf = rf

        vm = (value >> 17) & 1  # Virtual 8086 mode flag
        any_change |= getattr(self, "vm", vm) != vm
        self.vm = vm

        ac = (value >> 18) & 1  # Alignment check / Access control flag
        any_change |= getattr(self, "ac", ac) != ac
        self.ac = ac

        vif = (value >> 19) & 1  # Virtual interrupt flag
        any_change |= getattr(self, "vif", vif) != vif
        self.vif = vif

        vip = (value >> 20) & 1  # Virtual interrupt pending flag
        any_change |= getattr(self, "vip", vip) != vip
        self.vip = vip

        id = (value >> 21) & 1  # ID flag
        any_change |= getattr(self, "id", id) != id
        self.id = id

        # Status flags
        cf = value & 1  # Carry flag
        any_change |= getattr(self, "cf", cf) != cf
        self.cf = cf

        pf = (value >> 2) & 1  # Parity flag
        any_change |= getattr(self, "pf", pf) != pf
        self.pf = pf

        af = (value >> 4) & 1  # Auxiliary carry flag
        any_change |= getattr(self, "af", af) != af
        self.af = af

        zf = (value >> 6) & 1  # Zero flag
        any_change |= getattr(self, "zf", zf) != zf
        self.zf = zf

        sf = (value >> 7) & 1  # Sign flag
        any_change |= getattr(self, "sf", sf) != sf
        self.sf = sf

        of = (value >> 11) & 1  # Overflow flag
        any_change |= getattr(self, "of", of) != of
        self.of = of

        open_bracket = f"{self.options['text-secondary']}[{RESET_COLOR}"
        close_bracket = f"{self.options['text-secondary']}]{RESET_COLOR}"

        return (
            f"{self.options['text-highlight'] if any_change else self.options['text-secondary']}{self.name}{RESET_COLOR} "
            f"{open_bracket} {self.flag('DF', df)} {close_bracket} "
            f"{open_bracket} {self.flag('TF', tf)} {self.flag('IF', _if)} "
            f"{self.flag('IOPL', iopl)} {self.flag('NT', nt)} {self.flag('RF', rf)} "
            f"{self.flag('VM', vm)} {self.flag('AC', ac)} {self.flag('VIF', vif)} "
            f"{self.flag('VIP', vip)} {self.flag('ID', id)} {close_bracket} "
            f"{open_bracket} {self.flag('CF', cf)} {self.flag('PF', pf)} {self.flag('AF', af)} "
            f"{self.flag('ZF', zf)} {self.flag('SF', sf)} {self.flag('OF', of)} {close_bracket}"
        )


class MxcsrRegister(FlagsRegister):
    def get_value(self, frame):  # type: (gdb.Frame) -> str
        value = int(frame.read_register(self.descriptor))

        any_change = False

        # Sticky flags
        ie = value & 1  # Invalid operation flag
        any_change |= getattr(self, "ie", ie) != ie
        self.ie = ie

        de = (value >> 1) & 1  # Denormal flag
        any_change |= getattr(self, "de", de) != de
        self.de = de

        ze = (value >> 2) & 1  # Divide-by-zero flag
        any_change |= getattr(self, "ze", ze) != ze
        self.ze = ze

        oe = (value >> 3) & 1  # Overflow flag
        any_change |= getattr(self, "oe", oe) != oe
        self.oe = oe

        ue = (value >> 4) & 1  # Underflow flag
        any_change |= getattr(self, "ue", ue) != ue
        self.ue = ue

        pe = (value >> 5) & 1  # Precision flag
        any_change |= getattr(self, "pe", pe) != pe
        self.pe = pe

        # Floating-point exception mask bits
        daz = (value >> 6) & 1  # Denormals are zero
        any_change |= getattr(self, "daz", daz) != daz
        self.daz = daz

        im = (value >> 7) & 1  # Invalid operation mask
        any_change |= getattr(self, "im", im) != im
        self.im = im

        dm = (value >> 8) & 1  # Denormal mask
        any_change |= getattr(self, "dm", dm) != dm
        self.dm = dm

        zm = (value >> 9) & 1  # Divide-by-zero mask
        any_change |= getattr(self, "zm", zm) != zm
        self.zm = zm

        om = (value >> 10) & 1  # Overflow mask
        any_change |= getattr(self, "om", om) != om
        self.om = om

        um = (value >> 11) & 1  # Underflow mask
        any_change |= getattr(self, "um", um) != um
        self.um = um

        pm = (value >> 12) & 1  # Precision mask
        any_change |= getattr(self, "pm", pm) != pm
        self.pm = pm

        # Other
        rc = (value >> 13) & 3  # Rounding control
        any_change |= getattr(self, "rc", rc) != rc
        self.rc = rc

        ftz = (value >> 15) & 1  # Flush to zero
        any_change |= getattr(self, "ftz", ftz) != ftz
        self.ftz = ftz

        open_bracket = f"{self.options['text-secondary']}[{RESET_COLOR}"
        close_bracket = f"{self.options['text-secondary']}]{RESET_COLOR}"

        return (
            f"{self.options['text-highlight'] if any_change else self.options['text-secondary']}{self.name}{RESET_COLOR} "
            f"{open_bracket} {self.flag('FTZ', ftz)} {self.flag('RC', rc)} {close_bracket} "
            f"{open_bracket} {self.flag('PM', pm)} {self.flag('UM', um)} {self.flag('UM', um)} {self.flag('OM', om)} "
            f"{self.flag('ZM', zm)} {self.flag('DM', dm)} {self.flag('IM', im)} {self.flag('DAZ', daz)} {close_bracket} "
            f"{open_bracket} {self.flag('PE', pe)} {self.flag('UE', ue)} {self.flag('OE', oe)} "
            f"{self.flag('ZE', ze)} {self.flag('DE', de)} {self.flag('IE', ie)} {close_bracket}"
        )
