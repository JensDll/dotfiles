$env:Path += ";$env:XDG_DATA_HOME\lua-language-server-3.18.1-win32-x64\bin"

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
