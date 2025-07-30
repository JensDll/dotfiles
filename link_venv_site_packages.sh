#!/usr/bin/env bash

set -e

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null || exit
  pwd -P
)"
declare -r root unix="${root}/unix"

shopt -s expand_aliases

source "${unix}/.bash_aliases"

venv="$(pipenv --venv)"
declare -r venv

ln --symbolic --force "$(lldb -P)"/lldb "${venv}"/lib/python*/site-packages
if [[ $(gdb --eval-command 'show data-directory' --batch) =~ \"(.*)\" ]]; then
  ln --symbolic --force "${BASH_REMATCH[1]}"/python/gdb "${venv}"/lib/python*/site-packages
fi

set -x

ll "${venv}"/lib/python*/site-packages
