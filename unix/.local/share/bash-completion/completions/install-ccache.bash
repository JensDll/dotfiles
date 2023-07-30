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

  case "$prev" in
  --prefix)
    # Complete directories after prefix option
    _filedir -d
    ;;
  esac

  if [[ $cur = -* ]]; then
    # Needs not to be expanded
    # shellcheck disable=SC2016
    mapfile -t COMPREPLY < <(compgen -W '$(_parse_help "$1")' -- "$cur")
  fi
}

complete -F __start_install_ccache install-ccache
