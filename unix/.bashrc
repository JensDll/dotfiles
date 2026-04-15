if [[ -z ${PS1} ]]; then
  # skip when running non-interactive
  return
fi

HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000

shopt -s histappend
shopt -s checkwinsize

# shellcheck disable=SC2128,SC2178,SC2179,SC2309
push_back_prompt_command() {
  if [[ ";${PROMPT_COMMAND[*]};" == *";$1;"* ]]; then
    # already added
    return
  fi

  if [[ -z ${PROMPT_COMMAND[*]} ]]; then
    # no prompt command
    if [[ BASH_VERSINFO[0] -gt 5 || (BASH_VERSINFO[0] -eq 5 && BASH_VERSINFO[1] -ge 1) ]]; then
      # >= 5.1 array supported
      PROMPT_COMMAND=("$1")
    else
      PROMPT_COMMAND="$1"
    fi
  elif [[ $(builtin declare -p PROMPT_COMMAND 2> /dev/null) == 'declare -a'* ]]; then
    # is an array, append to it
    PROMPT_COMMAND+=("$1")
  else
    if ! [[ "${PROMPT_COMMAND}" =~ \;[[:space:]]*$ ]]; then
      # does not end with ';', need to append it
      PROMPT_COMMAND+=';'
    fi
    PROMPT_COMMAND+="$1"
  fi
}

push_back_prompt_command 'history -a'

unset -f push_back_prompt_command

if [[ ${TERM} = xterm-color || ${TERM} = *-256color ]]; then
  is_color=1
fi

if [[ -x /usr/bin/tput ]] && tput setaf 1> /dev/null 2>&1; then
  is_color=1
fi

if [[ -r ${HOME}/.git-prompt.sh ]]; then
  is_git=1
  source "${HOME}"/.git-prompt.sh
fi

if [[ is_color -eq 1 ]]; then
  if [[ is_git -eq 1 ]]; then
    PS1='\[\033[38;2;0;255;0m\]\u\[\033[38:5:15m\]:\[\033[38;2;83;234;253m\]\w\[\033[38;2;162;244;253m\]$(__git_ps1 "(%s)")\[\033[38;2;255;255;255m\]$ '
  else
    PS1='\[\033[38;2;0;255;0m\]\u\[\033[38:5:15m\]:\[\033[38;2;83;234;253m\]\w\[\033[38;2;255;255;255m\]$ '
  fi
  export COLORTERM=truecolor
else
  if [[ is_git -eq 1 ]]; then
    PS1='\u:\w$(__git_ps1 "(%s)")$ '
  else
    PS1='\u:\w$ '
  fi
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

if [[ ! ${PATH} =~ ${HOME}/.local/bin:${HOME}/bin ]]; then
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

if [[ ${OSTYPE} = darwin* ]]; then
  eval "$(locale)"
  if [[ -d /opt/homebrew ]]; then
    PATH=/opt/homebrew/bin:"${PATH}"
    source <(brew shellenv bash)
    if [[ -r /opt/homebrew/etc/profile.d/bash_completion.sh ]]; then
      source /opt/homebrew/etc/profile.d/bash_completion.sh
    fi
  fi
fi

if [[ -r ${HOME}/.bash_aliases ]]; then
  source "${HOME}"/.bash_aliases
fi

export CPM_SOURCE_CACHE="${HOME}"/.cache/cpm
export PATH
export PROMPT_COMMAND
