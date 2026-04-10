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

return M
