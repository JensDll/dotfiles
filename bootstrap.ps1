<#
.DESCRIPTION
Bootstrap Windows specific dotfiles.

.PARAMETER Dotfiles
Install dotfiles to predefined locations.

.PARAMETER Registry
Write registry configuration.

.PARAMETER Environment
Setup environment variables.

.PARAMETER DevDrive
Drive letter of the systems dev drive.
#>
[CmdletBinding()]
param(
  [switch]$Dotfiles,
  [switch]$Registry,
  [switch]$Environment,
  [char]$DevDrive = 'D'
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
  Copy-Item -Path "$PSScriptRoot\windows\nuget.config" -Destination "${env:APPDATA}\NuGet\NuGet.Config"
  New-Item -ItemType SymbolicLink -Target "$PSScriptRoot\unix\.config\nvim" -Path "${DevDrive}:\.config\nvim" -Force
}

function Install-Registry() {
  regedit.exe /s "$PSScriptRoot\windows\setup.reg"
}

function Install-Environment() {
  $path = [System.Environment]::GetEnvironmentVariable('Path', [System.EnvironmentVariableTarget]::User) -split ';'

  $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
  if (Test-Path $vswhere) {
    $vsInstallDir = & $vswhere -prerelease -property installationPath | Select-Object -First 1
    [System.Environment]::SetEnvironmentVariable('VSINSTALLDIR', "$vsInstallDir\", [System.EnvironmentVariableTarget]::User)
    if ($path -notcontains "${vsInstallDir}\Common7\Tools\") {
      $path += "${vsInstallDir}\Common7\Tools\"
    }
  }

  if ($path -notcontains "${DevDrive}:\.local\bin\") {
    $path += "${DevDrive}:\.local\bin\"
  }

  [System.Environment]::SetEnvironmentVariable('Path', $path -join ';', [System.EnvironmentVariableTarget]::User)

  [System.Environment]::SetEnvironmentVariable('TMP', "${DevDrive}:\tmp", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('TEMP', "${DevDrive}:\tmp", [System.EnvironmentVariableTarget]::User)

  $cacheDir = "${DevDrive}:\.cache"

  [System.Environment]::SetEnvironmentVariable('XDG_CONFIG_HOME', "${DevDrive}:\.config", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_DATA_HOME', "${DevDrive}:\.local\share", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_STATE_HOME', "${DevDrive}:\.local\state", [System.EnvironmentVariableTarget]::User)
  [System.Environment]::SetEnvironmentVariable('XDG_CACHE_HOME', "$cacheDir", [System.EnvironmentVariableTarget]::User)

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

if ($Dotfiles) {
  Install-Dotfiles
  $installedAny = $true
}

if (-not $installedAny) {
  Install-Environment
  Install-Dotfiles
  Install-Registry
}
