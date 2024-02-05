# shellcheck disable=SC2148
# shellcheck disable=SC1090
# shellcheck disable=SC1091
# shellcheck shell=sh

if [ -n "$BASH_VERSION" ]; then
  if [ -f "$HOME/.bashrc" ]; then
    . "$HOME/.bashrc"
  fi
fi

if [ -d "$HOME/bin" ]; then
  PATH="$HOME/bin:$PATH"
fi

if [ -d "$HOME/.local/bin" ]; then
  PATH="$HOME/.local/bin:$PATH"
fi

if [ -f "$HOME/.cargo/env" ]; then
  PATH="$HOME/.cargo/bin:$PATH"
fi

PATH="/opt/texlive/2023/bin/x86_64-linux:$PATH:/home/jens/.local/share/JetBrains/Toolbox/scripts"

export PATH
