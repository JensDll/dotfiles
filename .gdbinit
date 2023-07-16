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

set $COLOR_RED = "\e[30;1;31m"
set $COLOR_GREEN = "\e[30;1;32m"
set $COLOR_YELLOW = "\e[30;1;33m"
set $COLOR_BLUE = "\e[30;1;34m"
set $COLOR_MAGENTA = "\e[30;1;35m"
set $COLOR_RESET = "\e[0m"

define print_register
if ($argc % 4 == 0)
  set $_rows = 4
end

if ($argc % 5 == 0)
  set $_rows = 5
end

set $_blocks = ($argc / $_rows) - 1

set $_i = 0
set $_j = 0

# 64-bit registers
while ($_i < $_blocks)
  eval "set $_name = $arg%d", $_j
  eval "set $_r64_%d = (long)$%s", $_i, $_name
  eval "set $_r64 = $_r64_%d", $_i
  printf "%4s %s%016lx%s %-20ld\t", $_name, $COLOR_BLUE, $_r64, $COLOR_RESET, $_r64
  set $_i++
  set $_j++
end
eval "set $_name = $arg%d", $_j
eval "set $_r64_%d = (long)$%s", $_i, $_name
eval "set $_r64 = $_r64_%d", $_i
printf "%4s %s%016lx%s %-20ld\n", $_name, $COLOR_BLUE, $_r64, $COLOR_RESET, $_r64
set $_i = 0
set $_j++

# 32-bit registers
while ($_i < $_blocks)
  eval "set $_name = $arg%d", $_j
  eval "set $_r32h_%d = $_r64_%d >> 32", $_i, $_i
  eval "set $_r32h = $_r32h_%d", $_i
  eval "set $_r32l_%d = $_r64_%d & 0xffffffff", $_i, $_i
  eval "set $_r32l = $_r32l_%d", $_i
  printf "%4s %08x%s%08x%s %-20u\t", $_name, $_r32h, $COLOR_BLUE, $_r32l, $COLOR_RESET, $_r32l
  set $_i++
  set $_j++
end
eval "set $_name = $arg%d", $_j
eval "set $_r32h_%d = $_r64_%d >> 32", $_i, $_i
eval "set $_r32h = $_r32h_%d", $_i
eval "set $_r32l_%d = $_r64_%d & 0xffffffff", $_i, $_i
eval "set $_r32l = $_r32l_%d", $_i
printf "%4s %08x%s%08x%s %-20u\n", $_name, $_r32h, $COLOR_BLUE, $_r32l, $COLOR_RESET, $_r32l
set $_i = 0
set $_j++

# 16-bit registers
while ($_i < $_blocks)
  eval "set $_name = $arg%d", $_j
  eval "set $_r32h = $_r32h_%d", $_i
  eval "set $_r16h_%d = $_r32l_%d >> 16", $_i, $_i
  eval "set $_r16h = $_r16h_%d", $_i
  eval "set $_r16l_%d = $_r32l_%d & 0xffff", $_i, $_i
  eval "set $_r16l = $_r16l_%d", $_i
  printf "%4s %08x%04x%s%04x%s %-20u\t", $_name, $_r32h, $_r16h, $COLOR_BLUE, $_r16l, $COLOR_RESET, $_r16l
  set $_i++
  set $_j++
end
eval "set $_name = $arg%d", $_j
eval "set $_r32h = $_r32h_%d", $_i
eval "set $_r16h_%d = $_r32l_%d >> 16", $_i, $_i
eval "set $_r16h = $_r16h_%d", $_i
eval "set $_r16l_%d = $_r32l_%d & 0xffff", $_i, $_i
eval "set $_r16l = $_r16l_%d", $_i
printf "%4s %08x%04x%s%04x%s %-20u\n", $_name, $_r32h, $_r16h, $COLOR_BLUE, $_r16l, $COLOR_RESET, $_r16l
set $_i = 0
set $_j++

if ($_rows == 5)
  # Upper 8-bit registers
  while ($_i < $_blocks)
    eval "set $_name = $arg%d", $_j
    eval "set $_r32h = $_r32h_%d", $_i
    eval "set $_r16h = $_r16h_%d", $_i
    eval "set $_r8h = $_r16l_%d >> 8", $_i
    eval "set $_r8l = $_r16l_%d & 0xff", $_i
    printf "%4s %08x%04x%s%02x%s%02x %-20u\t", $_name, $_r32h, $_r16h, $COLOR_BLUE, $_r8h, $COLOR_RESET, $_r8l, $_r8h
    set $_i++
    set $_j++
  end
  eval "set $_name = $arg%d", $_j
  eval "set $_r32h = $_r32h_%d", $_i
  eval "set $_r16h = $_r16h_%d", $_i
  eval "set $_r8h = $_r16l_%d >> 8", $_i
  eval "set $_r8l = $_r16l_%d & 0xff", $_i
  printf "%4s %08x%04x%s%02x%s%02x %-20u\n", $_name, $_r32h, $_r16h, $COLOR_BLUE, $_r8h, $COLOR_RESET, $_r8l, $_r8h
  set $_i = 0
  set $_j++
end

# Lower 8-bit registers
while ($_i < $_blocks)
  eval "set $_name = $arg%d", $_j
  eval "set $_r32h = $_r32h_%d", $_i
  eval "set $_r16h = $_r16h_%d", $_i
  eval "set $_r8h = $_r16l_%d >> 8", $_i
  eval "set $_r8l = $_r16l_%d & 0xff", $_i
  printf "%4s %08x%04x%02x%s%02x%s %-20u\t", $_name, $_r32h, $_r16h, $_r8h, $COLOR_BLUE, $_r8l, $COLOR_RESET, $_r8l
  set $_i++
  set $_j++
end
eval "set $_name = $arg%d", $_j
eval "set $_r32h = $_r32h_%d", $_i
eval "set $_r16h = $_r16h_%d", $_i
eval "set $_r8h = $_r16l_%d >> 8", $_i
eval "set $_r8l = $_r16l_%d & 0xff", $_i
printf "%4s %08x%04x%02x%s%02x%s %-20u\n", $_name, $_r32h, $_r16h, $_r8h, $COLOR_BLUE, $_r8l, $COLOR_RESET, $_r8l
end

define registers
print_register "rax" "rcx" "rdx" "rbx" "eax" "ecx" "edx" "ebx" "ax" "cx" "dx" "bx" "ah" "ch" "dh" "bh" "al" "cl" "dl" "bl"
echo \n
print_register "rsp" "rbp" "rsi" "rdi" "esp" "ebp" "esi" "edi" "sp" "bp" "si" "di" "spl" "bpl" "sil" "dil"
echo \n
print_register "r8" "r9" "r10" "r11" "r8d" "r9d" "r10d" "r11d" "r8w" "r9w" "r10w" "r11w" "r8b" "r9b" "r10b" "r11b"
echo \n
print_register "r12" "r13" "r14" "r15" "r12d" "r13d" "r14d" "r15d" "r12w" "r13w" "r14w" "r15w" "r12b" "r13b" "r14b" "r15b"
end
document registers
print registers information to the screen
end

define context
printf "--------------------------------- [registers]\n"
end
document context
print context information to the screen
end
