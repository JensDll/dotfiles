# shellcheck shell=bash

declare -r reset="\033[0m"
declare -r red="\033[0;31m"
declare -r green="\033[0;32m"

# shellcheck disable=SC2034
# shellcheck disable=SC2155
declare -rl id=$(uname)

__success() {
  echo -e "${green}$*${reset}"
}

__error() {
  echo -e "${red}Error: $*${reset}" 1>&2
}

__error_and_exit() {
  echo -e "${red}Error: $*${reset}" 1>&2
  exit 1
}
