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

usage() {
  cat << EOF
Usage: ${program} <action> [options]

  <action> = home
  The type of action to perform:
    - home
      Bootstrap the local unix directory into the user's home directory.
    - udev
      Keyboard rules.
    - arch
      Arch Linux related config.

  --? | --help
  Print this message and exit.

  --yes
  Don't ask for permission.
EOF
  exit "${1:-2}"
}

parse_parameters() {
  local -a arguments

  yes=0

  while [[ $# -gt 0 ]]; do
    local -l option="${1/#--/-}"

    case "${option}" in
    -\? | -h | -he | -hel | -help)
      usage 0
      ;;
    -y | -ye | -yes)
      yes=1
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      arguments+=("$1")
      ;;
    esac

    shift
  done

  action=${arguments[0]:-home}
}

parse_parameters "$@"
declare -r action
declare -r yes

bootstrap_home() {
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
  if [[ yes -eq 1 ]]; then
    bootstrap_home
  else
    read -r -p 'This may overwrite existing files in your home directory. Are you sure? (Y/n) '
    declare -rl yes_no="${REPLY:-y}"
    if [[ ${yes_no} = y ]]; then
      bootstrap_home
    fi
  fi
  ;;
u | ud | ude | udev)
  set -x
  sudo cp "${misc}"/*.hwdb /usr/lib/udev/hwdb.d
  sudo systemd-hwdb update
  sudo udevadm trigger
  ;;
a | ar | arc | arch)
  set -x
  sudo install -m 644 -t /etc "${misc}"/mkinitcpio.conf "${misc}"/pacman.conf
  sudo install -m 755 "${misc}"/arch-kernel-install /usr/local/bin/arch-kernel-install
  sudo install -D -m 644 -t /etc/pacman.d/hooks/ \
    "${misc}"/90-kernel-install.hook \
    "${misc}"/90-kernel-remove.hook
  for hook in /usr/share/libalpm/hooks/*mkinitcpio*; do
    sudo ln -s -f /dev/null /etc/pacman.d/hooks/"${hook##*/}"
  done
  ;;
*)
  echo "Unknown action: ${action}"
  usage
  ;;
esac
