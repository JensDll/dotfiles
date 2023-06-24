#!/usr/bin/env bash

root="$(
  cd "$(dirname "$0")/.." > /dev/null 2>&1 || exit 1
  pwd -P
)"
declare -r root

shfmt -w "$root" .bash_aliases .bash_logout .bashrc .profile
