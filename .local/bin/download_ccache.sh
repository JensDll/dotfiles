#!/usr/bin/bash

# To run directly from source, use the following command
# and replace <version> with the ccache version:
# bash -s - <version> <<< "$(curl --location --fail --silent --show-error https://raw.githubusercontent.com/JensDll/dotfiles/main/.local/bin/download_ccache.sh)"

# https://ccache.dev

declare -r reset="\033[0m"
declare -r red="\033[0;31m"
declare -r green="\033[0;32m"

__usage() {
	# https://manpages.debian.org/coreutils/cat
	cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") <version> [options]
Options: [defaults in brackets after descriptions]
  --help|-h|-?      print this message
  --install-dir     directory in which to install   [$HOME/.local/bin]
EOF

	if [[ $1 != --no-exit ]]; then
		exit 2
	fi
}

__success() {
	# https://manpages.debian.org/coreutils/echo
	echo -e "${green}Success: $*${reset}"
}

__error() {
	echo -e "${red}Error: $*${reset}" 1>&2
}

__error_and_exit() {
	echo -e "${red}Error: $*${reset}" 1>&2
	exit 1
}

__cleanup() {
	echo "Cleaning up temporary directory: $1"
	# https://manpages.debian.org/coreutils/rm
	rm --recursive "$1"
}

__check_option() {
	[[ -z $1 ]] && __error "Missing value for option $2" && __usage
}

############ ARGUMENTS ############
declare -r version=${1#v}
[[ -z $version ]] && __error "Missing value for argument <version>" && __usage
############ ARGUMENTS ############

############ OPTIONS ############
install_dir="$HOME/.local/bin"

while [[ $# -gt 0 ]]; do
	declare -l option="${1/#--/-}"

	case "$option" in
	-\? | -help | -h)
		__usage --no-exit
		exit 0
		;;
	-install-dir)
		shift
		install_dir="$1"
		;;
	-install-dir=*)
		install_dir="${option#*=}"
		;;
	esac

	shift
done

declare -r install_dir

__check_option "$install_dir" '--install-dir'
############ OPTIONS ############

# https://manpages.debian.org/coreutils/mktemp
temp_dir=$(mktemp --directory)
declare -r temp_dir

# https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html#index-trap
trap '__cleanup $temp_dir' EXIT

# https://manpages.debian.org/gpg/gpg
if ! gpg --list-public-keys '5A939A71A46792CF57866A51996DDA075594ADB8' >/dev/null 2>&1; then
	gpg --keyserver hkps://keyserver.ubuntu.com --receive-keys '5A939A71A46792CF57866A51996DDA075594ADB8'
fi

declare -r binary="ccache-$version-linux-x86_64.tar.xz"
declare -r binary_uri="https://github.com/ccache/ccache/releases/download/v$version/$binary"
declare -r binary_output="$temp_dir/$binary"

declare -r signature="ccache-$version-linux-x86_64.tar.xz.asc"
declare -r signature_uri="https://github.com/ccache/ccache/releases/download/v$version/$signature"
declare -r signature_output="$temp_dir/$signature"

# https://manpages.debian.org/curl/curl
if ! curl --location --fail --fail-early \
	--output "$signature_output" "$signature_uri" \
	--output "$binary_output" "$binary_uri"; then
	__error_and_exit "Failed to download ccache binary and signature"
fi

if ! gpg --verify "$signature_output" "$binary_output"; then
	__error_and_exit "Signature verification failed"
fi

# https://manpages.debian.org/tar/tar
tar --extract --xz --file "$binary_output" --directory "$temp_dir"

declare -r executable="${binary_output%.tar.xz}/ccache"

# https://manpages.debian.org/coreutils/mkdir
mkdir --parents "$install_dir"
# https://manpages.debian.org/coreutils/mv
mv --target-directory="$install_dir" "$executable"

__success "Installed $executable to $install_dir"
