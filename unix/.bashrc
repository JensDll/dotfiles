# shellcheck disable=SC2148
# shellcheck disable=SC1090
# shellcheck disable=SC1091

# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#Is-this-Shell-Interactive_003f
if [[ -z $PS1 ]]; then
  # Skip when running non-interactive
  return
fi

# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-HISTCONTROL
HISTCONTROL=ignoreboth
# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-HISTSIZE
HISTSIZE=1000
# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-HISTFILESIZE
HISTFILESIZE=2000

# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-shopt
shopt -s histappend
shopt -s checkwinsize

# https://manpages.debian.org/lesspipe
[[ -x /usr/bin/lesspipe ]] && eval "$(SHELL=/bin/sh lesspipe)"

[[ -z ${debian_chroot:-} && -r /etc/debian_chroot ]] && debian_chroot=$(cat /etc/debian_chroot)

[[ $TERM = xterm-color || $TERM = *-256color ]] && color_prompt=yes

# https://manpages.debian.org/tput
# https://manpages.debian.org/terminfo
[[ -x /usr/bin/tput ]] && tput setaf 1> /dev/null 2>&1 && color_prompt=yes

# https://docs.brew.sh
if [[ -f /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
  source /opt/homebrew/etc/bash_completion.d/git-prompt.sh
fi

# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-PS1
# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#Controlling-the-Prompt
#   \u  The username of the current user
#   \h  The hostname up to the first '.'
#   \w  The value of the PWD shell variable, with $HOME abbreviated with a tilde (uses the $PROMPT_DIRTRIM variable)
#   \[  Begin a sequence of non-printing characters
#   \]  End a sequence of non-printing characters
# See https://en.wikipedia.org/wiki/ANSI_escape_code for information about the ANSI color syntax
if [[ $color_prompt = yes ]]; then
  PS1='${debian_chroot:+($debian_chroot)}\[\033[1;32m\]\u@\h\[\033[00m\]:\[\033[1;34m\]\w\[\033[36m\]$(__git_ps1 "(%s)")\[\033[00m\]\$ '
  export COLORTERM=truecolor
else
  PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi

[[ $TERM = xterm* || $TERM = rxvt* ]] && PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"

unset color_prompt

if [[ -x /usr/bin/dircolors ]]; then
  # https://manpages.debian.org/dircolors
  if [[ -r $HOME/.dircolors ]]; then
    eval "$(dircolors --bourne-shell "$HOME/.dircolors")"
  else
    eval "$(dircolors --bourne-shell)"
  fi
fi

# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-shopt
if ! shopt -oq posix; then
  if [[ -f /usr/share/bash-completion/bash_completion ]]; then
    source /usr/share/bash-completion/bash_completion
  elif [[ -f /etc/bash_completion ]]; then
    source /etc/bash_completion
  fi
fi

if [[ -f $HOME/.bash_aliases ]]; then
  source "$HOME/.bash_aliases"
fi

export NVM_DIR="$HOME/.nvm"
[[ -s $NVM_DIR/nvm.sh ]] && source "$NVM_DIR/nvm.sh"
[[ -s $NVM_DIR/bash_completion ]] && source "$NVM_DIR/bash_completion"

export PYENV_ROOT="$HOME/.pyenv"
if [[ -d $PYENV_ROOT ]]; then
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init -)"
fi

export GVM_DIR="$HOME/.gvm"
[[ -s "$GVM_DIR/scripts/gvm" ]] && source "$GVM_DIR/scripts/gvm"

export CPM_SOURCE_CACHE="$HOME/.cache/CPM"
