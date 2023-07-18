python
import os
import sys
import pathlib
config_home = os.environ.get("XDG_CONFIG_HOME") or pathlib.Path.home() / ".config"
sys.path.insert(0, str(config_home / "gdbdash"))
import gdbdash
gdbdash.start()
end

# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Messages_002fWarnings.html#Messages_002fWarnings
set confirm off
set verbose off
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Screen-Size.html#Screen-Size
set pagination off
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Command-History.html#Command-History
set history save on
set history expansion on
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Print-Settings.html#Print-Settings
set print pretty on
set print array off
set print array-indexes on
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Machine-Code.html#Machine-Code
set disassembly-flavor intel
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Python-Commands.html#Python-Commands
set python print-stack full

define cls
shell clear
end
document cls
clear the screen
end
