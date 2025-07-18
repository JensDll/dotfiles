#!/usr/bin/env bash

set -e

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null || exit
  pwd -P
)"
declare -r root unix="${root}"/unix

__bootstrap() {
  chmod 700 "${unix}"/.gnupg
  rsync --no-perms --archive --verbose --human-readable --safe-links --copy-links --exclude-from="${root}"/.rsyncignore "${unix}"/ "${HOME}"
  ln --symbolic --force "${unix}"/.config/* ~/.config/
}

if [[ $1 = --yes || $1 = -y ]]; then
  __bootstrap
else
  read -r -p 'This may overwrite existing files in your home directory. Are you sure? (Y/n) '

  declare -l reply="${REPLY:-y}"

  if [[ ${reply} = y ]]; then
    __bootstrap
  fi
fi
