local M = {}

---@class pses.user_config
---@field pses? pses.user_config.pses
---@field root_markers? string[]

---@class pses.user_config.pses
---@field path? string
---@field log_level? 'Trace'|'Debug'|'Information'|'Warning'|'Error'|'Critical'|'None'
---@field log_path? string
---@field session_path? string

---@class pses.config
---@field pses pses.user_config.pses
---@field root_markers string[]

---@class pses.config.pses
---@field path string
---@field log_level 'Trace'|'Debug'|'Information'|'Warning'|'Error'|'Critical'|'None'
---@field log_path? string
---@field session_path string

---@type pses.config
M.default_config = {
  pses = {
    path = vim.fs.joinpath(
      vim.env.XDG_DATA_HOME or vim.fs.joinpath(vim.env.HOME, '.local', 'share'),
      'PowerShellEditorServices'
    ),
    log_level = 'Warning',
    session_path = 'pses_session.json',
  },
  root_markers = { 'PSScriptAnalyzerSettings.psd1', '.git' },
}

M.config = {} --[[@as any]] --[[@as pses.config]]

M.augroup = vim.api.nvim_create_augroup('pses', {})

return M
