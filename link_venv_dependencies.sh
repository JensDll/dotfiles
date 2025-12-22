#!/usr/bin/env bash

set -e

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null || exit
  pwd -P
)"
declare -r root venv="${root}"/.venv

shopt -s expand_aliases

source "${root}/unix/.bash_aliases"

ln --symbolic --force "$(lldb -P)"/lldb "${venv}"/lib/python*/site-packages

set -x

ll "${venv}"/lib/python*/site-packages
