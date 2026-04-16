function Get-Git-Branch {
  $branch = git rev-parse --abbrev-ref HEAD 2> $null

  if ($LASTEXITCODE -ne 0) {
    return ''
  }

  if ($branch -eq 'HEAD') {
    $branch = git rev-parse --short HEAD
    return '{0}({1}){2}' -f $PSStyle.Foreground.Red, $branch, $PSStyle.Foreground.White
  } else {
    return '{0}({1}){2}' -f $PSStyle.Foreground.Cyan, $branch, $PSStyle.Foreground.White
  }
}

function prompt {
  $location = $ExecutionContext.SessionState.Path.CurrentLocation

  if (Get-Command -Name git -CommandType Application -ErrorAction SilentlyContinue) {
    $branch = Get-Git-Branch
  } else {
    $branch = ''
  }

  if ($location.Provider.Name -eq 'FileSystem') {
    # https://conemu.github.io/en/AnsiEscapeCodes.html#OSC_Operating_system_commands
    $cwd = "`e]9;9;`"{0}`"`e\" -f $location.ProviderPath
  } else {
    $cwd = ''
  }


  if (Test-Path -Path env:VSCMD_ARG_TGT_ARCH) {
    $arch = '{0}({1}){2}' -f $PSStyle.Foreground.Yellow, $env:VSCMD_ARG_TGT_ARCH, $PSStyle.Foreground.White
  } else {
    $arch = ''
  }

  return '{0}{1}{2}{3}{4}{5}$ ' -f $cwd, $PSStyle.Foreground.Green, $location, $PSStyle.Foreground.White, $branch, $arch
}

if (Get-Command -Name dotnet -CommandType Application -ErrorAction SilentlyContinue) {
  $version = dotnet --version
  $version = $version -split '\.'
  if ([int]$version[0] -ge 10) {
    dotnet completions script pwsh | Out-String | Invoke-Expression
  } else {
    Register-ArgumentCompleter -Native -CommandName dotnet -ScriptBlock {
      param($wordToComplete, $commandAst, $cursorPosition)
      dotnet complete --position $cursorPosition $commandAst | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
      }
    }
  }
}

$path = ($env:path -split ';').Where{ $_ }

if ($resolvedPath = Resolve-Path -Path "${env:XDG_DATA_HOME}\lua-language-server*\bin" -ErrorAction SilentlyContinue) {
  $path += $resolvedPath
}

if (Test-Path -Path "${env:ProgramFiles}\LLVM\bin") {
  $path += "${env:ProgramFiles}\LLVM\bin"
}

if (Test-Path -Path "${env:XDG_DATA_HOME}\omnisharp-win-x64-net6.0") {
  $path += "${env:XDG_DATA_HOME}\omnisharp-win-x64-net6.0"
}

if ($resolvedPath = Resolve-Path -Path '\opt\neovim\bin' -ErrorAction SilentlyContinue) {
  $path += $resolvedPath
  $env:GIT_EDITOR = 'nvim'
}

$env:path = $path -join ';'
