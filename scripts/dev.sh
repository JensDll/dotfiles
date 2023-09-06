#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.." > /dev/null 2>&1 || exit
  pwd -P
)"
declare -r root
declare -r unix="$root/unix"

rm -rf ~/.config/gdbdash
ln -s "${unix}"/.config/gdbdash ~/.config/gdbdash
