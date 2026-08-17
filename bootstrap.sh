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
        Configuration in home from ./unix
      - udev
        Udev configuration in /etc/udev
      - root
        Miscellaneous configuration in /usr and /etc

  --? | --help
    Print this message and exit
EOF
  exit "${1:-2}"
}

parse_parameters() {
  local -a args

  yes=0

  while [[ $# -gt 0 ]]; do
    local -l option="${1/#--/-}"

    case "${option}" in
    -\? | -h | -he | -hel | -help)
      usage 0
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      args+=("$1")
      ;;
    esac

    shift
  done

  action=${args[0]:-home}
}

parse_parameters "$@"
declare -r action

case "${action}" in
h | ho | hom | home)
  rsync \
    --archive \
    --verbose \
    --human-readable \
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
  ;;
u | ud | ude | udev)
  set -x
  sudo install -m 644 -t /etc/udev/hwdb.d "${misc}"/*.hwdb
  sudo install -m 644 -t /etc/udev/rules.d "${misc}"/*.rules
  sudo systemd-hwdb update
  sudo udevadm trigger
  ;;
r | ro | roo | root)
  set -x

  sudo install -m 644 -t /etc "${misc}"/pacman.conf
  sudo install -m 644 -t /etc "${misc}"/fstab

  sudo install -m 644 -t /etc/mkinitcpio.conf.d "${misc}"/90-mkinitcpio.conf

  sudo install -m 644 -t /etc/modules-load.d "${misc}"/zram.conf

  sudo install -D -m 644 -t /etc/systemd/user.conf.d "${misc}"/default-timeout.conf

  sudo install -D -m 644 -t /etc/pacman.d "${misc}"/mirrorlist
  sudo install -D -m 644 -t /etc/pacman.d/hooks "${misc}"/*.hook

  sudo install -m 755 -t /usr/local/bin "${misc}"/arch-kernel-install

  for hook in /usr/share/libalpm/hooks/*mkinitcpio*; do
    sudo ln -s -f /dev/null /etc/pacman.d/hooks/"${hook##*/}"
  done
  ;;
*)
  echo "Unknown action: ${action}"
  usage
  ;;
esac
