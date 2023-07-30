__install_ccache_debug() {
  if [[ -n ${BASH_COMP_DEBUG_FILE:-} ]]; then
    echo "$*" >>"$BASH_COMP_DEBUG_FILE"
  fi
}

__start_install_ccache() {
  local cur prev words cword

  _init_completion || return

  __install_ccache_debug
  __install_ccache_debug '========= starting install-ccache completion logic =========='
  __install_ccache_debug "cur = $cur, prev = $prev, words[*] = ${words[*]}, #words[@] = ${#words[@]}, cword is $cword"

  if [[ $cur = -* ]]; then
    # shellcheck disable=SC2016
    mapfile -t COMPREPLY < <(compgen -W '$(_parse_help "$1")' -- "$cur")
  fi
}

complete -o default -F __start_install_ccache install-ccache
