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
  [Alias('Y')]
  [Parameter(ParameterSetName = 'Dotfiles')]
  [switch]$Yes,
  [Parameter(ParameterSetName = 'Registry')]
  [switch]$Registry,
  [Parameter(ParameterSetName = 'Environment')]
  [switch]$Environment
)

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

if ($Yes) {
  Install-Dotfiles
  return
}

while ($true) {
  $result = Read-Host -Prompt 'This may overwrite existing files in your home directory. Are you sure? (Y/n)'
  $result = $result.ToLower()

  if ($result -eq 'n') {
    return
  } elseif ($result -eq 'y' -or [string]::IsNullOrWhiteSpace($result)) {
    Install-Dotfiles
    return
  } else {
    Write-Host 'Please answer y or n.'
  }
}
