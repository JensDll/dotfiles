has() {
  builtin type -fP "$1" &> /dev/null
}

if [[ ${OSTYPE} = linux-gnu ]]; then
  alias ls='ls --color=auto -F --group-directories-first'
  alias ll='ls -A -l'
elif [[ ${OSTYPE} = darwin* ]]; then
  alias ls='ls --color=auto -F'
  alias ll='ls -A -l'
fi

if ! has poweroff; then
  alias poweroff='sudo shutdown -h now'
fi

if ! has reboot; then
  alias reboot='sudo shutdown -r now'
fi

if has hyprshutdown; then
  alias hpoweroff="hyprshutdown -t 'Shutting down...' -p 'systemctl poweroff'"
  alias hsleep="hyprshutdown -t 'Sleeping...' -p 'systemctl sleep'"
  alias hreboot="hyprshutdown -t 'Restarting...' -p 'systemctl reboot'"
fi

alias lt='tree --dirsfirst -C -L 1 -apug'

alias grep='grep --color=auto'

alias cls='clear'

alias gdb='gdb --quiet'

alias today='date +%d.%m.%y'

alias his='history'

if has pacman; then
  alias pc='sudo pacman'
  if [[ -r /usr/share/bash-completion/completions/pacman ]]; then
    source /usr/share/bash-completion/completions/pacman
    complete -F _pacman pc
  fi
fi

if has kubectl; then
  alias k=kubectl
  source <(kubectl completion bash)
  complete -F __start_kubectl k
fi

if has helm; then
  alias h=helm
  source <(helm completion bash)
  complete -F __start_helm h
fi

if has linode_cli; then
  source <(linode-cli completion bash)
fi

if has pip; then
  source <(pip completion --bash)
fi

if has pnpm; then
  source <(pnpm completion bash)
  complete -F _pnpm_completion pnpm
fi

if has nvim; then
  export GIT_EDITOR='nvim'
  alias vi='nvim'
  alias vim='nvim'
fi

if has flatpak; then
  alias fp='flatpak'

  if flatpak list --app --columns=application 2> /dev/null | grep io.neovim.nvim > /dev/null; then
    export GIT_EDITOR='flatpak run io.neovim.nvim'
    alias vi='flatpak run io.neovim.nvim'
    alias vim='flatpak run io.neovim.nvim'
    alias nvim='flatpak run io.neovim.nvim'
  fi

  if [[ -r /usr/share/bash-completion/completions/flatpak ]]; then
    source /usr/share/bash-completion/completions/flatpak
    complete -o nospace -F __flatpak fp
  fi
fi

if has tree-sitter; then
  alias ts='tree-sitter'
fi

unset -f has
