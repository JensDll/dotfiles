# https://www.gnu.org/software/bash/manual/bash.html#Is-this-Shell-Interactive_003f
if [[ -z ${PS1} ]]; then
  # Skip when running non-interactive
  return
fi

__has() {
  builtin type -fP "$1" &> /dev/null
}

# https://www.gnu.org/software/bash/manual/bash.html#index-HISTCONTROL
HISTCONTROL=ignoreboth
# https://www.gnu.org/software/bash/manual/bash.html#index-HISTSIZE
HISTSIZE=1000
# https://www.gnu.org/software/bash/manual/bash.html#index-HISTFILESIZE
HISTFILESIZE=2000

# https://www.gnu.org/software/bash/manual/bash.html#index-shopt
shopt -s histappend
shopt -s checkwinsize

export PROMPT_COMMAND='history -a'

[[ -z ${debian_chroot:-} && -r /etc/debian_chroot ]] && debian_chroot=$(cat /etc/debian_chroot)

[[ ${TERM} = xterm-color || ${TERM} = *-256color ]] && color_prompt=yes

[[ -x /usr/bin/tput ]] && tput setaf 1> /dev/null 2>&1 && color_prompt=yes

# https://www.gnu.org/software/bash/manual/bash.html#index-PS1
# https://www.gnu.org/software/bash/manual/bash.html#Controlling-the-Prompt
#   \u  The username of the current user
#   \h  The hostname up to the first '.'
#   \w  The value of the PWD shell variable, with $HOME abbreviated with a tilde (uses the $PROMPT_DIRTRIM variable)
#   \[  Begin a sequence of non-printing characters
#   \]  End a sequence of non-printing characters
# See https://en.wikipedia.org/wiki/ANSI_escape_code for information about the ANSI color syntax
if [[ ${color_prompt} = yes ]]; then
  PS1='${debian_chroot:+($debian_chroot)}\[\033[38:5:10m\]\u@\h\[\033[38:5:15m\]:\[\033[38:5:12m\]\w\[\033[38:5:14m\]$(__git_ps1 "(%s)")\[\033[38:5:15m\]\$ '
  export COLORTERM=truecolor
else
  PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi

[[ ${TERM} = xterm* || ${TERM} = rxvt* ]] && PS1="\[\e]0;${debian_chroot:+(${debian_chroot})}\u@\h: \w\a\]${PS1}"

unset color_prompt

if [[ -x /usr/bin/dircolors ]]; then
  if [[ -r ${HOME}/.dircolors ]]; then
    eval "$(dircolors --bourne-shell "${HOME}/.dircolors")"
  else
    eval "$(dircolors --bourne-shell)"
  fi
fi

if ! shopt -oq posix; then
  if [[ -f /usr/share/bash-completion/bash_completion ]]; then
    source /usr/share/bash-completion/bash_completion
  elif [[ -f /etc/bash_completion ]]; then
    source /etc/bash_completion
  fi
fi

if [[ -d /opt/nvim-linux-x86_64 ]]; then
  PATH=/opt/nvim-linux-x86_64/bin:"${PATH}"
fi

if [[ -d ${HOME}/.nvm ]]; then
  export NVM_DIR="${HOME}"/.nvm

  if [[ -f ${NVM_DIR}/nvm.sh ]]; then
    source "${NVM_DIR}"/nvm.sh
  fi

  if [[ -f ${NVM_DIR}/bash_completion ]]; then
    source "${NVM_DIR}"/bash_completion
  fi
fi

if [[ -d ${HOME}/.pyenv ]]; then
  export PYENV_ROOT="${HOME}"/.pyenv
  PATH="${PYENV_ROOT}"/bin:"${PATH}"
  eval "$(pyenv init -)"
fi

if [[ -d ${HOME}/.gvm ]]; then
  source "${HOME}"/.gvm/scripts/gvm
fi

if [[ -f ${HOME}/.bash_aliases ]]; then
  source "${HOME}"/.bash_aliases
fi

export CPM_SOURCE_CACHE="${HOME}"/.cache/CPM

export PATH
