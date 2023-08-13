<#
.DESCRIPTION
Bootstrap Windows specific dotfiles.

.PARAMETER Yes
Do not prompt for confirmation.

.PARAMETER Registry
Install the registry setup file.
#>
[CmdletBinding(DefaultParameterSetName = 'Dotfiles')]
param(
  [Parameter(ParameterSetName = 'Dotfiles')]
  [switch]$Dotfiles,
  [Parameter(ParameterSetName = 'Registry')]
  [switch]$Registry,
  [Parameter(ParameterSetName = 'Environment')]
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
  # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
  [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', "$HOME\.local\share", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', "$HOME\.config", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_STATE_HOME', "$HOME\.local\state", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', "$HOME\.cache", [System.EnvironmentVariableTarget]::User)
}

if ($Registry) {
  Install-Registry
  return
}

if ($Environment) {
  Install-Environment
  return
}

if ($Dotfiles) {
  Install-Dotfiles
  return
}

Install-Environment
Install-Dotfiles
Install-Registry
