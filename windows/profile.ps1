function prompt {
  $location = $ExecutionContext.SessionState.Path.CurrentLocation;

  $out = ''

  if ($location.Provider.Name -eq 'FileSystem') {
    # https://conemu.github.io/en/AnsiEscapeCodes.html#OSC_Operating_system_commands
    $out += "`e]9;9;`"{0}`"`e\" -f $location.ProviderPath
  }

  $out += 'PS {0}{1} ' -f $location, '>' * ($NestedPromptLevel + 1)

  return $out
}

if (Get-Command -Name dotnet -CommandType Application -ErrorAction SilentlyContinue) {
  $version = dotnet --version
  $version = $version -split '\.'
  if ([int]$version[0] -ge 10) {
    dotnet completions script pwsh | Out-String | Invoke-Expression
  } else {
    Register-ArgumentCompleter -Native -CommandName dotnet -ScriptBlock {
      param($wordToComplete, $commandAst, $cursorPosition)
      dotnet complete --position $cursorPosition "$commandAst" | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
      }
    }
  }
}

$path = ($env:path -split ';').Where{ $_ }

if ($resolvedPath = Resolve-Path -Path "${env:XDG_DATA_HOME}\lua-language-server*\bin\") {
  $path += "$resolvedPath"
}

if (Test-Path -Path "${env:ProgramFiles}\LLVM\bin\") {
  $path += "${env:ProgramFiles}\LLVM\bin\"
}

if (Test-Path -Path "${env:XDG_DATA_HOME}\omnisharp-win-x64-net6.0\") {
  $path += "${env:XDG_DATA_HOME}\omnisharp-win-x64-net6.0\"
}

$env:path = $path -join ';'
