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
  [switch]$Registry
)

function Install-Dotfiles() {
  Copy-Item -Path "$PSScriptRoot\windows\profile.ps1" -Destination $PROFILE -Verbose
  Get-ChildItem -Path "$PSScriptRoot\unix" -File | Select-Object -ExpandProperty FullName | Copy-Item -Destination $HOME -Verbose
}

function Install-Registry() {
  regedit.exe /s "$PSScriptRoot\windows\setup.reg"
}

if (-not $IsWindows) {
  Write-Error 'This script is only for Windows.'
  return
}

if ($Registry) {
  Install-Registry
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
