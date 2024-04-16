#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.." > /dev/null 2>&1 || exit
  pwd -P
)"
declare -r root
declare -r unix="$root/unix"

shopt -s expand_aliases

# shellcheck source=../unix/.bash_aliases
source "$unix/.bash_aliases"

pushd "$root" > /dev/null || exit

python -m venv .venv

ln --symbolic --force "$(lldb -P)"/lldb ./.venv/lib/python*/site-packages
if [[ $(gdb --eval-command 'show data-directory' --batch) =~ \"(.*)\" ]]; then
  ln --symbolic --force "${BASH_REMATCH[1]}"/python/gdb ./.venv/lib/python*/site-packages
fi

popd > /dev/null || exit
