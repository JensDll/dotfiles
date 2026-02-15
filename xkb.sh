#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null || exit
  pwd -P
)"
declare -r root xkb="${root}"/unix/.config/xkb

xkbcomp -I"${xkb}" "${xkb}"/map "${DISPLAY}"
