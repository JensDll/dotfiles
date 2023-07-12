#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 || exit
  pwd -P
)"
declare -r root

shopt -s expand_aliases

source "$root/.bash_aliases"

__bootstrap() {
  # https://manpages.debian.org/rsync/rsync
  rsync --no-perms --archive --verbose --human-readable \
    --exclude '.git/' \
    --exclude '.github/' \
    --exclude 'scripts/' \
    --exclude 'bootstrap.sh' \
    --exclude 'texlive2023profile' \
    "$root/" "$HOME"

  if type -f nvim > /dev/null 2>&1; then
    # https://neovim.io/doc/user/builtin.html#writefile()
    local -r nvim_config_home=$(nvim --noplugin --headless -c 'call writefile([stdpath("config")], "/dev/stdout", "b") | q')
    local -r default_nvim_config_home="$HOME/.config/nvim"

    if [[ $nvim_config_home != "$default_nvim_config_home" ]]; then
      # https://manpages.debian.org/coreutils/ln
      ln --symbolic --verbose --no-dereference --force "$default_nvim_config_home" "$nvim_config_home"
    fi
  fi
}

if [[ $1 = --yes || $1 = -y ]]; then
  __bootstrap
else
  # https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-read
  read -r -p 'This may overwrite existing files in your home directory. Are you sure? (Y/n) '

  declare -l reply="${REPLY:-y}"

  if [[ $reply = y ]]; then
    __bootstrap
  fi
fi
