if [[ -z ${PS1} ]]; then
  # Skip when running non-interactive
  return
fi

HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000

shopt -s histappend
shopt -s checkwinsize

if [[ -z ${debian_chroot:-} && -r /etc/debian_chroot ]]; then
  debian_chroot=$(cat /etc/debian_chroot)
fi

if [[ ${TERM} = xterm-color || ${TERM} = *-256color ]]; then
  is_color=true
fi

if [[ -x /usr/bin/tput ]] && tput setaf 1> /dev/null 2>&1; then
  is_color=true
fi

if [[ -r ${HOME}/.git-prompt.sh ]]; then
  is_git=true
  source "${HOME}"/.git-prompt.sh
fi

if [[ ${is_color} = true ]]; then
  if [[ ${is_git} = true ]]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[38:5:10m\]\u@\h\[\033[38:5:15m\]:\[\033[38:5:12m\]\w\[\033[38:5:14m\]$(__git_ps1 "(%s)")\[\033[38:5:15m\]\$ '
  else
    PS1='${debian_chroot:+($debian_chroot)}\[\033[38:5:10m\]\u@\h\[\033[38:5:15m\]:\[\033[38:5:12m\]\w\[\033[38:5:14m\]\[\033[38:5:15m\]\$ '
  fi
  export COLORTERM=truecolor
else
  PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi

unset is_color
unset is_git

if [[ -x /usr/bin/dircolors ]]; then
  if [[ -r ${HOME}/.dircolors ]]; then
    eval "$(dircolors --bourne-shell "${HOME}/.dircolors")"
  else
    eval "$(dircolors --bourne-shell)"
  fi
fi

if ! shopt -oq posix; then
  if [[ -r /usr/share/bash-completion/bash_completion ]]; then
    source /usr/share/bash-completion/bash_completion
  elif [[ -r /etc/bash_completion ]]; then
    source /etc/bash_completion
  fi
fi

if ! [[ ${PATH} =~ ${HOME}/.local/bin:${HOME}/bin ]]; then
  PATH="${HOME}"/.local/bin:"${HOME}"/bin:"${PATH}"
fi

if [[ -d /opt/nvim-linux-x86_64 ]]; then
  PATH=/opt/nvim-linux-x86_64/bin:"${PATH}"
fi

if [[ -d ${HOME}/.nvm ]]; then
  export NVM_DIR="${HOME}"/.nvm

  if [[ -r ${NVM_DIR}/nvm.sh ]]; then
    source "${NVM_DIR}"/nvm.sh
  fi

  if [[ -r ${NVM_DIR}/bash_completion ]]; then
    source "${NVM_DIR}"/bash_completion
  fi
fi

if [[ -d ${HOME}/.gvm ]]; then
  source "${HOME}"/.gvm/scripts/gvm
fi

if [[ -d ${HOME}/.deno ]]; then
  source "${HOME}/.deno/env"
  source <(deno completions bash)
  export DENO_NO_UPDATE_CHECK=1
fi

if [[ -r ${HOME}/.bash_aliases ]]; then
  source "${HOME}"/.bash_aliases
fi

export CPM_SOURCE_CACHE="${HOME}"/.cache/CPM
export PATH
export PROMPT_COMMAND
