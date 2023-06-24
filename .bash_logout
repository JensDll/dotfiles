# shellcheck disable=SC2148
# shellcheck disable=SC1090
# shellcheck disable=SC1091

# https://www.gnu.org/savannah-checkouts/gnu/bash/manual/bash.html#index-SHLVL
if [[ "$SHLVL" = 1 ]]; then
  [[ -x /usr/bin/clear_console ]] && /usr/bin/clear_console -q
fi
