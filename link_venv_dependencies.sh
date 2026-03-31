#!/usr/bin/env bash

set -e

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null || exit
  pwd -P
)"
declare -r root
declare -r venv="${root}"/.venv

shopt -s expand_aliases

source "${root}/unix/.bash_aliases"

set -x

ln -s -f "$(lldb -P)"/lldb "${venv}"/lib/python*/site-packages
