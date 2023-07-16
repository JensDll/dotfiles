# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Prompt.html#Prompt
set prompt \033[38;5;177mgdb\033[0m$ 
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Messages_002fWarnings.html#Messages_002fWarnings
set confirm off
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Screen-Size.html#Screen-Size
set pagination off
# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Command-History.html#Command-History
set history save on
set history expansion on

# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Machine-Code.html#Machine-Code
set disassembly-flavor intel

# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Define.html#Define
define cls
shell clear
end
document cls
clear the screen
end

# https://sourceware.org/gdb/current/onlinedocs/gdb.html/Hooks.html#Hooks
define hook-stop
end
