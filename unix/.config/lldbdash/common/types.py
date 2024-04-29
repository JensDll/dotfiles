import lldb
from lldbdash.commands import Command

Settings = dict[str, Command]

Output = lldb.SBStream | lldb.SBCommandReturnObject
