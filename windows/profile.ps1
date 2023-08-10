Import-Module posh-git
$GitPromptSettings.BranchIdenticalStatusSymbol = ''

oh-my-posh init pwsh --config "$env:XDG_CONFIG_HOME\oh-my-posh\config.json" | Invoke-Expression
