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
#>
[CmdletBinding()]
param(
  [switch]$Config,
  [switch]$Registry,
  [switch]$Environment,
  [char]$DriveLetter = 'D'
)

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
    if ($path -notcontains "${vsInstallDir}\Common7\Tools\") {
      $path += "${vsInstallDir}\Common7\Tools\"
    }
  }

  if ($path -notcontains "${DriveLetter}:\.local\bin\") {
    $path += "${DriveLetter}:\.local\bin\"
  }

  [System.Environment]::SetEnvironmentVariable('Path', $path -join ';', [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('TMP', "${DriveLetter}:\tmp", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('TEMP', "${DriveLetter}:\tmp", [System.EnvironmentVariableTarget]::User)

  $cacheDir = "${DriveLetter}:\.cache"

  [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', "${DriveLetter}:\.config", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', "${DriveLetter}:\.local\share", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_STATE_HOME', "${DriveLetter}:\.local\state", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', $cacheDir, [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('CPM_SOURCE_CACHE', "${cacheDir}\cpm", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('DENO_DIR', "${cacheDir}\deno", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('UV_CACHE_DIR', "${cacheDir}\uv", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('VCPKG_DEFAULT_BINARY_CACHE ', "${cacheDir}\vcpkg", [System.EnvironmentVariableTarget]::User)
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
