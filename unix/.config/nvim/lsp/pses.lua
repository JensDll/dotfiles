local config = {
  pses = {
    path = vim.fs.joinpath(
      vim.env.XDG_DATA_HOME or vim.fs.joinpath(vim.env.HOME, '.local', 'share'),
      'PowerShellEditorServices'
    ),
    log_level = 'Warning',
    session_details_path = 'pses_session.json',
  },
}

---@type vim.lsp.Config
return {
  name = 'pses',
  cmd = function(dispatchers, config) end,
  root_markers = {
    'PSScriptAnalyzerSettings.psd1',
    '.git',
  },
}
