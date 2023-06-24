#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.." > /dev/null 2>&1 || exit 1
  pwd -P
)"
declare -r root

shellcheck "$root"/*.sh "$root"/scripts/*.sh "$root"/.local/bin/*.sh \
  "$root/.bash_aliases" "$root/.bash_logout" "$root/.bashrc" "$root/.profile"
