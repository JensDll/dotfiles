__has() {
  builtin type -fP "$1" &> /dev/null
}

if [[ ${OSTYPE} = linux-gnu ]]; then
  alias ls='ls --color=auto -F --group-directories-first'
  alias ll='ls -A -l'
elif [[ ${OSTYPE} = darwin* ]]; then
  alias ls='ls --color=auto -F'
  alias ll='ls -A -l'
fi

if ! __has poweroff; then
  alias poweroff='sudo shutdown -h now'
fi

if ! __has reboot; then
  alias reboot='sudo shutdown -r now'
fi

alias lt='tree --dirsfirst -C -L 1 -apug'

alias grep='grep --color=auto'

alias cls='clear'

alias gdb='gdb --quiet'

alias today='date +%d.%m.%y'

alias his='history'

for i in {24..18}; do
  if __has lldb-"${i}"; then
    # shellcheck disable=SC2139
    alias lldb="lldb-${i}"
    break
  fi
done

if __has kubectl; then
  alias k=kubectl
  source <(kubectl completion bash)
  complete -F __start_kubectl k
fi

if __has helm; then
  alias h=helm
  source <(helm completion bash)
  complete -F __start_helm h
fi

if __has linode_cli; then
  source <(linode-cli completion bash)
fi

if __has pip; then
  source <(pip completion --bash)
fi

if __has pnpm; then
  source <(pnpm completion bash)
  complete -F _pnpm_completion pnpm
fi

if __has nvim; then
  export GIT_EDITOR='nvim'
  alias vi='nvim'
  alias vim='nvim'
fi

if __has flatpak; then
  alias fp='flatpak'

  if flatpak list --app --columns=application 2> /dev/null | grep io.neovim.nvim > /dev/null; then
    export GIT_EDITOR='flatpak run io.neovim.nvim'
    alias vi='flatpak run io.neovim.nvim'
    alias vim='flatpak run io.neovim.nvim'
    alias nvim='flatpak run io.neovim.nvim'
  fi

  if [[ -f /usr/share/bash-completion/completions/flatpak ]]; then
    source /usr/share/bash-completion/completions/flatpak
    complete -o nospace -F __flatpak fp
  fi
fi
