local M = {
  OS_LINUX = 0,
  OS_WINDOWS = 1,
  OS_MAC = 2,
  DOTFILES_AUGROUP = vim.api.nvim_create_augroup('dotfiles', {}),
}

local os_type = function()
  local sysname = vim.uv.os_uname().sysname

  if sysname == 'Linux' then
    return M.OS_LINUX
  end

  if sysname == 'Windows_NT' then
    return M.OS_WINDOWS
  end

  return M.OS_MAC
end

M.OS = os_type()

---@param t table
M.ivalues = function(t)
  local i = 0
  return function()
    i = i + 1
    return t[i]
  end
end

M.shift_f12 = function()
  if M.OS == M.OS_LINUX then
    return '<F24>'
  end
  return '<S-F12>'
end

M.ctrl_shift_f12 = function()
  if M.OS == M.OS_LINUX then
    return '<F48>'
  end
  return '<C-S-F12>'
end

M.ctrl_f5 = function()
  if M.OS == M.OS_LINUX then
    return '<F17>'
  end
  return '<C-F5>'
end

return M
