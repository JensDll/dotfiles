#!/usr/bin/env bash

set -e

declare -r program=${BASH_SOURCE[0]}

usage() {
  cat << EOF
Usage: ${program} <path> [<tree-ish>] [options]

  <path>
  Path to the source.

  <tree-ish>
  Tree-ish git object for when <path> is a git repository.

  --? | --help
  Print this message and exit.
EOF
  exit "${1:-2}"
}

parse_parameters() {
  local -a args

  while [[ $# -gt 0 ]]; do
    local -l option="${1/#--/-}"

    case "${option}" in
    -\? | -h | -he | -hel | -help)
      usage 0
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      args+=("$1")
      ;;
    esac

    shift
  done

  path="${args[0]}"
  tree_ish="${args[1]}"

  if [[ -z ${path} ]]; then
    echo "Missing required argument <path>"
    usage
  fi

  if git -C "${path}" rev-parse --is-inside-work-tree &> /dev/null; then
    is_git=1
    if [[ -z ${tree_ish} ]]; then
      echo "Missing required argument <tree-ish>"
      usage
    fi
  fi
}

parse_parameters "$@"

declare -r path
declare -r tree_ish
declare -r is_git

if [[ is_git -eq 1 ]]; then
  git -c core.abbrev=no -C "${path}" archive --format tar "${tree_ish}" | sha512sum
elif [[ -f ${path} ]]; then
  sha512sum "${path}"
else
  echo "The path ${path} is neither a git repository nor a regular file"
fi
