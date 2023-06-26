#!/usr/bin/env bash

source="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 || exit 1
  pwd -P
)/"
declare -r source

__bootstrap() {
  # https://manpages.debian.org/rsync/rsync
  rsync --no-perms --archive --verbose --human-readable \
    --exclude '.git/' \
    --exclude '.github/' \
    --exclude 'scripts/' \
    --exclude 'bootstrap.sh' \
    "$source" "$HOME";
}

if [[ $1 = --yes || $1 = -y ]]; then
  __bootstrap
else
  # https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-read
  read -r -p 'This may overwrite existing files in your home directory. Are you sure? (Y/n) '

  declare -l REPLY="${REPLY:-y}"

  if [[ $REPLY = y ]]; then
    __bootstrap
  fi
fi
