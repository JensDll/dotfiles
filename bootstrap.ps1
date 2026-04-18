<#
.DESCRIPTION
Bootstrap Windows specific items.

.PARAMETER Config
Install config files to predefined locations.

.PARAMETER Registry
Write registry configuration.

.PARAMETER Environment
Setup environment variables.

.PARAMETER DriveLetter
The root path of various files and environment variables.
For example a Dev Drive disk partition.
#>
[CmdletBinding()]
param(
  [switch]$Config,
  [switch]$Registry,
  [switch]$Environment,
  [char]$DriveLetter = 'D'
)

Set-StrictMode -Version 3.0

if (-not $IsWindows) {
  Write-Error 'This script is only for Windows.'
  return
}

function Install-Config() {
  New-Item -ItemType File -Path $PROFILE -Force
  Copy-Item -Path "${PSScriptRoot}\windows\profile.ps1" -Destination $PROFILE
  Copy-Item -Path "${PSScriptRoot}\windows\terminal.json" -Destination `
    "${env:LOCALAPPDATA}\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
  Copy-Item -Path "${PSScriptRoot}\windows\nuget.config" -Destination "${env:APPDATA}\NuGet\NuGet.Config"
  Copy-Item -Path "${PSScriptRoot}\unix\.gitconfig" -Destination '~\.gitconfig'
  New-Item -ItemType SymbolicLink -Target "${PSScriptRoot}\unix\.config\nvim" `
    -Path "${DriveLetter}:\.config\nvim" -Force
}

function Install-Registry() {
  regedit.exe /s "${PSScriptRoot}\windows\setup.reg"
}

function Install-Environment() {
  $path = [System.Environment]::GetEnvironmentVariable('Path', [System.EnvironmentVariableTarget]::User) -split ';'

  $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
  if (Test-Path $vswhere) {
    $vsInstallDir = & $vswhere -prerelease -property installationPath | Select-Object -First 1
    [System.Environment]::SetEnvironmentVariable('VSINSTALLDIR', "${vsInstallDir}\", [System.EnvironmentVariableTarget]::User)
    if ($path -notcontains "${vsInstallDir}\Common7\Tools") {
      $path += "${vsInstallDir}\Common7\Tools"
    }
  }

  $localBin = "${DriveLetter}:\.local\bin"
  $configHome = "${DriveLetter}:\.config"
  $dataHome = "${DriveLetter}:\.local\share"
  $stateHome = "${DriveLetter}:\.local\state"
  $cacheHome = "${DriveLetter}:\.cache"

  if ($path -notcontains $localBin) {
    $path += $localBin
  }

  [System.Environment]::SetEnvironmentVariable('Path', $path -join ';', [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('TMP', "${DriveLetter}:\tmp", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('TEMP', "${DriveLetter}:\tmp", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', $configHome, [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', $dataHome, [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_STATE_HOME', $stateHome, [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', $cacheHome, [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('CPM_SOURCE_CACHE', "${cacheHome}\cpm", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('DENO_DIR', "${cacheHome}\deno", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('VCPKG_DEFAULT_BINARY_CACHE ', "${cacheHome}\vcpkg", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('DOTNET_CLI_TELEMETRY_OPTOUT ', 'true', [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('UV_CACHE_DIR', "${cacheHome}\uv", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('UV_PYTHON_BIN_DIR', $localBin, [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('UV_PYTHON_INSTALL_DIR', "${dataHome}\uv\python", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('UV_TOOL_BIN_DIR', $localBin, [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('UV_TOOL_DIR', "${dataHome}\uv\tools", [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('NUGET_HTTP_CACHE_PATH', "${cacheHome}\nuget\v3", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('NUGET_PLUGINS_CACHE_PATH', "${cacheHome}\nuget\plugins", [System.EnvironmentVariableTarget]::User)
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

if ($Config) {
  Install-Config
  $installedAny = $true
}

if (-not $installedAny) {
  Install-Environment
  Install-Config
  Install-Registry
}
