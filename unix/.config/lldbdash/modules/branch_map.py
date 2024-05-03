import typing

from .register import RegisterReader, RflagsRegister

DoesBranch = typing.Callable[
    [RflagsRegister, RegisterReader],
    int,
]

above: DoesBranch = lambda flags, _: not flags.cf and not flags.zf
above_equal: DoesBranch = lambda flags, _: not flags.cf
below: DoesBranch = lambda flags, _: flags.cf
below_equal: DoesBranch = lambda flags, _: flags.cf or flags.zf
carry: DoesBranch = lambda flags, _: flags.cf
equal: DoesBranch = lambda flags, _: flags.zf
greater: DoesBranch = lambda flags, _: not flags.zf and flags.sf == flags.of
greater_equal: DoesBranch = lambda flags, _: flags.sf == flags.of
less: DoesBranch = lambda flags, _: flags.sf != flags.of
less_equal: DoesBranch = lambda flags, _: flags.zf or flags.sf != flags.of
not_above: DoesBranch = lambda flags, _: flags.cf or flags.zf
not_above_equal: DoesBranch = lambda flags, _: flags.cf
not_below: DoesBranch = lambda flags, _: not flags.cf
not_below_equal: DoesBranch = lambda flags, _: not flags.cf and not flags.zf
not_carry: DoesBranch = lambda flags, _: not flags.cf
not_equal: DoesBranch = lambda flags, _: not flags.zf
not_greater: DoesBranch = lambda flags, _: flags.zf or flags.sf != flags.of
not_greater_equal: DoesBranch = lambda flags, _: flags.sf != flags.of
not_less: DoesBranch = lambda flags, _: flags.sf == flags.of
not_less_equal: DoesBranch = lambda flags, _: not flags.zf and flags.sf == flags.of
not_overflow: DoesBranch = lambda flags, _: not flags.of
not_parity: DoesBranch = lambda flags, _: not flags.pf
not_sign: DoesBranch = lambda flags, _: not flags.sf
not_zero: DoesBranch = lambda flags, _: not flags.zf
overflow: DoesBranch = lambda flags, _: flags.of
parity: DoesBranch = lambda flags, _: flags.pf
parity_even: DoesBranch = lambda flags, _: flags.pf
parity_odd: DoesBranch = lambda flags, _: not flags.pf
sign: DoesBranch = lambda flags, _: flags.sf
zero: DoesBranch = lambda flags, _: flags.zf

BRANCH_MAP: dict[str, DoesBranch] = {
    "ja": above,
    "jae": above_equal,
    "jb": below,
    "jbe": below_equal,
    "jc": carry,
    "jcxz": lambda _, reader: reader.read_gp("cx").value == 0,
    "jecxz": lambda _, reader: reader.read_gp("ecx").value == 0,
    "jrcxz": lambda _, reader: reader.read_gp("rcx").value == 0,
    "je": equal,
    "jg": greater,
    "jge": greater_equal,
    "jl": less,
    "jle": less_equal,
    "jna": not_above,
    "jnae": not_above_equal,
    "jnb": not_below,
    "jnbe": not_below_equal,
    "jnc": not_carry,
    "jne": not_equal,
    "jng": not_greater,
    "jnge": not_greater_equal,
    "jnl": not_less,
    "jnle": not_less_equal,
    "jno": not_overflow,
    "jnp": not_parity,
    "jns": not_sign,
    "jnz": not_zero,
    "jo": overflow,
    "jp": parity,
    "jpe": parity_even,
    "jpo": parity_odd,
    "js": sign,
    "jz": zero,
    "cmova": above,
    "cmovae": above_equal,
    "cmovb": below,
    "cmovbe": below_equal,
    "cmovc": carry,
    "cmove": equal,
    "cmovg": greater,
    "cmovge": greater_equal,
    "cmovl": less,
    "cmovle": less_equal,
    "cmovna": not_above,
    "cmovnae": not_above_equal,
    "cmovnb": not_below,
    "cmovnbe": not_below_equal,
    "cmovnc": not_carry,
    "cmovne": not_equal,
    "cmovng": not_greater,
    "cmovnge": not_greater_equal,
    "cmovnl": not_less,
    "cmovnle": not_less_equal,
    "cmovno": not_overflow,
    "cmovnp": not_parity,
    "cmovns": not_sign,
    "cmovnz": not_zero,
    "cmovo": overflow,
    "cmovp": parity,
    "cmovpe": parity_even,
    "cmovpo": parity_odd,
    "cmovs": sign,
    "cmovz": zero,
}
