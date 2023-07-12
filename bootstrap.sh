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
  rsync --no-perms --archive --verbose --human-readable --exclude-from="$root/.rsyncignore" "$root/" "$HOME"

  # https://neovim.io/doc/user/builtin.html#writefile()
  # https://neovim.io/doc/user/builtin.html#stdpath()

  if type -f nvim > /dev/null 2>&1; then
    local -r nvim_config_home=$(nvim --noplugin --headless --cmd 'call writefile([stdpath("config")], "/dev/stdout", "b") | q')
    local -r default_nvim_config_home="$HOME/.config/nvim"

    local -r nvim_data_home=$(nvim --noplugin --headless --cmd 'call writefile([stdpath("data")], "/dev/stdout", "b") | q')
    local -r default_nvim_data_home="$HOME/.local/share/nvim"

    if [[ $default_nvim_config_home != "$nvim_config_home" ]]; then
      rsync --no-perms --archive --verbose --human-readable --exclude-from="$root/.rsyncignore" "$default_nvim_config_home/" "$nvim_config_home"
    fi

    if [[ $default_nvim_data_home != "$nvim_data_home" ]]; then
      rsync --no-perms --archive --verbose --human-readable --exclude-from="$root/.rsyncignore" "$default_nvim_data_home/" "$nvim_data_home"
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
