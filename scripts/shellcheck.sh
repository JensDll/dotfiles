#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.." > /dev/null 2>&1 || exit
  pwd -P
)"
declare -r root
declare -r unix="$root/unix"

shellcheck --external-sources "$root"/**/*.sh "$unix"/.local/bin/* "$unix"/.local/share/bash-completion/completions/* \
  "$unix/.bash_aliases" "$unix/.bash_logout" "$unix/.bashrc" "$unix/.profile"
