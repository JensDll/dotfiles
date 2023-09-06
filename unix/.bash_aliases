# shellcheck disable=SC2148
# shellcheck disable=SC1090
# shellcheck disable=SC1091

# https://manpages.debian.org/ls
alias ls='ls --color=auto -F --group-directories-first'
alias ll='ls --all -l'
alias la='ls --almost-all'

# https://manpages.debian.org/tree
alias lt='tree --dirsfirst -C -L 1 -a'

# https://manpages.debian.org/grep
alias grep='grep --color=auto'

# https://manpages.debian.org/clear
alias cls='clear'

# https://neovim.io/doc/user
if flatpak list --app --columns=application | grep io.neovim.nvim > /dev/null; then
  alias vi='flatpak run io.neovim.nvim'
  alias vim='flatpak run io.neovim.nvim'
  alias nvim='flatpak run io.neovim.nvim'
fi

# https://sourceware.org/gdb/documentation
alias gdb='gdb --quiet'

# Used like: `sleep 10; alert`
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-type

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
