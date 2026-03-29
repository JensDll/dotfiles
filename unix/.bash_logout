# shellcheck disable=SC2309
if [[ SHLVL -eq 1 ]]; then
  if [[ -x /usr/bin/clear_console ]]; then
    /usr/bin/clear_console -q
  fi
fi
