#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.." > /dev/null 2>&1 || exit
  pwd -P
)"
declare -r root

shfmt -w "$root" "$root/.bash_aliases" "$root/.bash_logout" "$root/.bashrc" "$root/.profile"
