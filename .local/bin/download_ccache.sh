#!/usr/bin/bash

# To run directly from GitHub, use the following command
# and replace <version> with the ccache version:
# bash -s - <version> <<< "$(curl --location https://raw.githubusercontent.com/JensDll/dotfiles/main/.local/bin/download_ccache.sh)"

# https://ccache.dev

declare -r reset="\033[0m"
declare -r red="\033[0;31m"
declare -r green="\033[0;32m"

declare -r version=${1#v}

# https://manpages.debian.org/mktemp
output_dir=$(mktemp --directory)
declare -r output_dir

__usage() {
  echo "Usage: $(basename "${BASH_SOURCE[0]}") <version>"
  exit 2
}

__success() {
  echo -e "${green}Success: $*${reset}"
}

__error() {
  echo -e "${red}Error: $*${reset}" 1>&2
  exit 1
}

__cleanup () {
  echo "Cleaning up temporary directory: $output_dir"
  # https://manpages.debian.org/rm
  rm --recursive "$output_dir"
}

# https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html#index-trap
trap __cleanup EXIT

if [[ -z $version ]]
then
  __usage
fi

# https://manpages.debian.org/gpg
if ! gpg --list-public-keys '5A939A71A46792CF57866A51996DDA075594ADB8' > /dev/null 2>&1
then
  gpg --keyserver hkps://keyserver.ubuntu.com --receive-keys '5A939A71A46792CF57866A51996DDA075594ADB8'
fi

declare -r binary="ccache-$version-linux-x86_64.tar.xz"
declare -r binary_uri="https://github.com/ccache/ccache/releases/download/v$version/$binary"
declare -r binary_output="$output_dir/$binary"

declare -r signature="ccache-$version-linux-x86_64.tar.xz.asc"
declare -r signature_uri="https://github.com/ccache/ccache/releases/download/v$version/$signature"
declare -r signature_output="$output_dir/$signature"

# https://manpages.debian.org/curl
curl --location \
  --output "$signature_output" "$signature_uri" \
  --output "$binary_output" "$binary_uri"

if ! gpg --verify "$signature_output" "$binary_output"
then
  __error "Signature verification failed"
fi

# https://manpages.debian.org/tar
tar --extract --xz --file "$binary_output" --directory "$output_dir"

declare -r executable="${binary_output%.tar.xz}/ccache"
declare -r executable_output="$HOME/.local/bin"

# https://manpages.debian.org/mv
mv --verbose "$executable" "$executable_output"

__success "Installed $executable to $executable_output"
