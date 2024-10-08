# shellcheck disable=SC2148
# shellcheck disable=SC1090
# shellcheck disable=SC1091

# https://manpages.debian.org/ls
if [[ $OSTYPE = linux-gnu ]]; then
  alias ls='ls --color=auto -F --group-directories-first'
  alias ll='ls -A -l'
elif [[ $OSTYPE = darwin* ]]; then
  alias ls='ls --color=auto -F'
  alias ll='ls -A -l'
fi

# https://www.gnu.org/software/bash/manual/bash.html#index-command
if ! command -v poweroff > /dev/null; then
  alias poweroff='sudo shutdown -h now'
fi

if ! command -v reboot > /dev/null; then
  alias reboot='sudo shutdown -r now'
fi

# https://manpages.debian.org/tree
alias lt='tree --dirsfirst -C -L 1 -apug'

# https://manpages.debian.org/grep
alias grep='grep --color=auto'

# https://manpages.debian.org/clear
alias cls='clear'

# https://neovim.io/doc/user
if flatpak list --app --columns=application 2> /dev/null | grep io.neovim.nvim > /dev/null; then
  alias vi='flatpak run io.neovim.nvim'
  alias vim='flatpak run io.neovim.nvim'
  alias nvim='flatpak run io.neovim.nvim'
fi

# https://sourceware.org/gdb/documentation
alias gdb='gdb --quiet'

# Used like: `sleep 10; alert`
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# https://manpages.debian.org/date
alias today='date +%d.%m.%y'

for i in {15..25}; do
  if [[ $(type -t lldb-"$i") = file ]]; then
    # shellcheck disable=SC2139
    # https://lldb.llvm.org/index.html
    alias lldb="lldb-$i"
    break
  fi
done

# https://www.gnu.org/software/bash/manual/bash.html#index-type
# https://www.gnu.org/software/bash/manual/bash.html#index-complete

if [[ $(type -t kubectl) = file ]]; then
  alias k=kubectl
  source <(kubectl completion bash)
  complete -F __start_kubectl k
fi

if [[ $(type -t helm) = file ]]; then
  alias h=helm
  source <(helm completion bash)
  complete -F __start_helm h
fi

if [[ $(type -t linode-cli) = file ]]; then
  source <(linode-cli completion bash)
fi

if [[ $(type -t pip) = file ]]; then
  source <(pip completion --bash)
fi

if [[ $(type -t pnpm) = file ]]; then
  source <(pnpm completion bash)
  if [[ $(type -t _pnpm_completion) = function ]]; then
    complete -F _pnpm_completion pnpm
  fi
fi

if [[ $(type -t flatpak) = file ]]; then
  alias fp='flatpak'
  if [[ -f /usr/share/bash-completion/completions/flatpak ]]; then
    source /usr/share/bash-completion/completions/flatpak
    complete -o nospace -F __flatpak fp
  fi
fi
