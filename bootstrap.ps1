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
  New-Item -ItemType File -Path $PROFILE -Force
  Copy-Item -Path "$PSScriptRoot\windows\profile.ps1" -Destination $PROFILE
  Copy-Item -Path "$PSScriptRoot\windows\terminal.json" `
    -Destination "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
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

  $devDrive = 'D'

  $path = [System.Environment]::GetEnvironmentVariable('Path', [System.EnvironmentVariableTarget]::User)

  if (-not (";$path;" -like "*;${devDrive}:\.local\bin;*")) {
    [System.Environment]::SetEnvironmentVariable('Path', "${path};D:\.local\bin", [System.EnvironmentVariableTarget]::User)
  }

  [System.Environment]::SetEnvironmentVariable('TMP', "${devDrive}:\tmp", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('TEMP', "${devDrive}:\tmp", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', "${devDrive}:\.config", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', "${devDrive}:\.local\share", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_STATE_HOME', "${devDrive}:\.local\state", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', "${devDrive}:\.cache", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('CPM_SOURCE_CACHE', "${devDrive}:\.cache\cpm", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('DENO_DIR', "${devDrive}:\.cache\deno", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('UV_CACHE_DIR', "${devDrive}:\.cache\uv", [System.EnvironmentVariableTarget]::User)
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
