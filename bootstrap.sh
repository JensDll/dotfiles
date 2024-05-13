#!/usr/bin/env bash

root="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 || exit
  pwd -P
)"
declare -r root
declare -r unix="$root/unix"

shopt -s expand_aliases

# shellcheck source=./unix/.bash_aliases
source "$unix/.bash_aliases"

__bootstrap() {
  chmod 700 "$unix/.gnupg"

  # https://manpages.debian.org/rsync/rsync
  rsync --no-perms --archive --verbose --human-readable --safe-links --copy-links --exclude-from="$root/.rsyncignore" "$unix/" "$HOME"

  if type -f nvim > /dev/null 2>&1; then
    __bootstrap_nvim
  fi
}

__bootstrap_nvim() {
  # https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-mapfile
  # https://neovim.io/doc/user/builtin.html#writefile()
  # https://neovim.io/doc/user/builtin.html#stdpath()
  mapfile -t < <(nvim --noplugin --headless --cmd 'call writefile([stdpath("config"), stdpath("data")], "/dev/stdout", "b")' --cmd 'quit')

  local -r nvim_config_home="${MAPFILE[0]}"
  local -r default_nvim_config_home="$HOME/.config/nvim"
  local -r local_nvim_config_home="$unix/.config/nvim"

  local -r nvim_data_home="${MAPFILE[1]}"
  local -r default_nvim_data_home="$HOME/.local/share/nvim"
  local -r local_nvim_data_home="$unix/.local/share/nvim"

  if [[ -d $local_nvim_config_home && $default_nvim_config_home != "$nvim_config_home"  ]]; then
    cat << EOF

[Neovim] Detected a non-default ($default_nvim_config_home) config directory, also copying files to: $nvim_config_home
[Neovim] See: https://neovim.io/doc/user/starting.html#standard-path
EOF

    rsync --no-perms --archive --safe-links --copy-links --human-readable "$default_nvim_config_home/" "$nvim_config_home"
  fi

  if [[ -d $local_nvim_data_home && $default_nvim_data_home != "$nvim_data_home" ]]; then
    cat << EOF

[Neovim] Detected a non-default ($default_nvim_data_home) data directory, also copying files to: $nvim_data_home
[Neovim] See: https://neovim.io/doc/user/starting.html#standard-path
EOF

    rsync --no-perms --archive --safe-links --copy-links --human-readable "$default_nvim_data_home/" "$nvim_data_home"
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
