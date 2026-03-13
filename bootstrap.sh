#!/usr/bin/env bash

set -e
shopt -s shift_verbose failglob

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null || exit
  pwd -P
)"
declare -r root
declare -r unix="${root}"/unix
declare -r misc="${root}"/misc
declare -r program=${BASH_SOURCE[0]}

__bs_echo() {
  echo "$*"
}

__bs_usage() {
  cat << EOF
Usage: ${program} <action> [options]

Arguments:

  <action> = home
  The type of action to perform. Action names can be abbreviated.
  - home
    Bootstrap the local unix directory into the user's home directory.
  - udev

Options:

  --help | -h | -?
  Print this message and exit.

  --yes | -y
  Don't ask for permission.
EOF
  exit "${1:-2}"
}

__bs_parse_parameters() {
  local -a arguments

  while [[ $# -gt 0 ]]; do
    local -l option="${1/#--/-}"

    case "${option}" in
    -\? | -h | -he | -hel | -help)
      __bs_usage 0
      ;;
    -y | -ye | -yes)
      yes=true
      ;;
    -*)
      __bs_echo "Unknown option: $1"
      __bs_usage
      ;;
    *)
      arguments+=("$1")
      ;;
    esac

    shift
  done

  action=${arguments[0]:-home}
}

__bs_parse_parameters "$@"
declare -r action
declare -r yes

__bs_bootstrap() {
  chmod 700 "${unix}"/.gnupg

  rsync \
    --no-perms \
    --archive \
    --verbose \
    --human-readable \
    --safe-links \
    --copy-links \
    --filter 'exclude /.config' \
    --filter 'exclude __pycache__/' \
    "${unix}"/ \
    "${HOME}"

  ln -s -f "${unix}"/.config/* ~/.config/

  if [[ ${OSTYPE} = darwin* ]]; then
    pushd "${unix}"/.config/ghostty
    ln -s -f config.ghostty.macos config.ghostty.macos.active
    popd
  fi
}

case "${action}" in
h | ho | hom | home)
  if [[ ${yes} == true ]]; then
    __bs_bootstrap
  else
    read -r -p 'This may overwrite existing files in your home directory. Are you sure? (Y/n) '
    declare -rl yes_no="${REPLY:-y}"
    if [[ ${yes_no} = y ]]; then
      __bs_bootstrap
    fi
  fi
  ;;
u | ud | ude | udev)
  set -x
  sudo cp "${misc}"/*.hwdb /usr/lib/udev/hwdb.d
  sudo systemd-hwdb update
  sudo udevadm trigger
  ;;
*)
  __bs_echo "Unknown action: ${action}"
  __bs_usage
  ;;
esac
