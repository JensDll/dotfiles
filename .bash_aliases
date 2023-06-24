# shellcheck disable=SC2148
# shellcheck disable=SC1090
# shellcheck disable=SC1091

# https://manpages.debian.org/ls
alias ls='ls --color=auto -F'
alias ll='ls --all -l'
alias la='ls --almost-all'

# https://manpages.debian.org/grep
alias grep='grep --color=auto'

# https://manpages.debian.org/clear
alias cls='clear'

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
