<#
.DESCRIPTION
Bootstrap Windows specific dotfiles.

.PARAMETER Dotfiles
Install dotfiles to predefined locations.

.PARAMETER Registry
Write registry configuration.

.PARAMETER Environment
Setup environment variables.
#>
[CmdletBinding(DefaultParameterSetName = 'Dotfiles')]
param(
  [switch]$Dotfiles,
  [switch]$Registry,
  [switch]$Environment
)

if (-not $IsWindows) {
  Write-Error 'This script is only for Windows.'
  return
}

function Install-Dotfiles() {
  Copy-Item -Path "$PSScriptRoot\windows\profile.ps1" -Destination $PROFILE -Verbose
  Copy-Item -Path "$PSScriptRoot\windows\.config" -Destination $HOME -Verbose -Recurse -Force
  Get-ChildItem -Path "$PSScriptRoot\unix" -File | Select-Object -ExpandProperty FullName | Copy-Item -Destination $HOME -Verbose
}

function Install-Registry() {
  regedit.exe /s "$PSScriptRoot\windows\setup.reg"
}

function Install-Environment() {
  $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"

  if (Test-Path $vswhere) {
    $vsInstallDir = & $vswhere -prerelease -property installationPath | Select-Object -First 1
    [System.Environment]::SetEnvironmentVariable('VSINSTALLDIR', "$vsInstallDir\", [System.EnvironmentVariableTarget]::User)
  }

  # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
  [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', "$HOME\.local\share", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', "$HOME\.config", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_STATE_HOME', "$HOME\.local\state", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', "$HOME\.cache", [System.EnvironmentVariableTarget]::User)

  # https://github.com/cpm-cmake/CPM.cmake
  [System.Environment]::SetEnvironmentVariable('CPM_SOURCE_CACHE', "$HOME\.cache\CPM", [System.EnvironmentVariableTarget]::User)
}

$installedAny = $false

if ($Registry) {
  Install-Registry
  $installedAny = $true
}

if ($Environment) {
  Install-Environment
  $installedAny = $true
}

if ($Dotfiles) {
  Install-Dotfiles
  $installedAny = $true
}

if (-not $installedAny) {
  Install-Environment
  Install-Dotfiles
  Install-Registry
}
