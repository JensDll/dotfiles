#!/usr/bin/env bash

script_root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 || exit
  pwd -P
)/"
declare -r script_root

shopt -s expand_aliases

# shellcheck source=/dev/null
source "$script_root/.bash_aliases"

__bootstrap() {
  # https://manpages.debian.org/rsync/rsync
  rsync --no-perms --archive --verbose --human-readable \
    --exclude '.git/' \
    --exclude '.github/' \
    --exclude 'scripts/' \
    --exclude 'bootstrap.sh' \
    "$script_root" "$HOME"

  if type -f nvim > /dev/null 2>&1; then
    local -r nvim_config_path=$(nvim --noplugin --headless -c 'call writefile([stdpath("config")], "/dev/stdout", "b") | q')
    ln --symbolic --verbose --no-dereference --force "$HOME/.config/nvim" "$nvim_config_path"
  fi
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
