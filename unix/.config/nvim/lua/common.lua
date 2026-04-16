local M = {}

local os_linux = 0
local os_windows = 1
local os_mac = 2

local os_type = function()
  local sysname = vim.uv.os_uname().sysname

  if sysname == 'Linux' then
    return os_linux
  end

  if sysname == 'Windows_NT' then
    return os_windows
  end

  return os_mac
end

local current_os = os_type()

M.is_linux = function()
  return current_os == os_linux
end

M.is_windows = function()
  return current_os == os_windows
end

M.is_mac = function()
  return current_os == os_mac
end

M.shift_f12 = function()
  if M.is_linux() then
    return '<F24>'
  end
  return '<S-F12>'
end

M.ctrl_shift_f12 = function()
  if M.is_linux() then
    return '<F48>'
  end
  return '<C-S-F12>'
end

M.ctrl_f5 = function()
  if M.is_linux() then
    return '<F29>'
  end
  return '<C-F5>'
end

M.augroup = vim.api.nvim_create_augroup('dotfiles', {})

M.config_path = vim.fn.resolve(vim.fn.stdpath('config'))

return M
