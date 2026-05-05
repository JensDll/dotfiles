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

M.ctrl_f6 = function()
  if M.is_linux() then
    return '<F30>'
  end
  return '<C-F6>'
end

M.ctrl_f9 = function()
  if M.is_linux() then
    return '<F33>'
  end
  return '<C-F9>'
end

M.augroup = vim.api.nvim_create_augroup('dotfiles', {})

M.config_path = vim.fs.normalize(vim.fn.resolve(vim.fn.stdpath('config')))

---@param args string
---@return string[]
M.parse_args_preserve_quotes = function(args)
  args = vim.fn.trim(args) .. ' '

  local result = {}
  local i = 1

  while i < string.len(args) do
    i = string.find(args, '%S', i) --[[@as integer]]

    local quote
    if string.byte(args, i) == string.byte("'") then
      quote = "'"
    elseif string.byte(args, i) == string.byte('"') then
      quote = '"'
    end

    if quote then
      local next_i = string.find(args, quote, i + 1, true)
      if not next_i then
        table.insert(result, string.sub(args, i) .. quote)
        return result
      end
      table.insert(result, string.sub(args, i, next_i))
      i = next_i + 2
    else
      local next_i = string.find(args, '%s', i)
      table.insert(result, string.sub(args, i, next_i - 1))
      i = next_i + 1
    end
  end

  return result
end

---@param args string
---@return string[]
M.parse_args = function(args)
  args = vim.fn.trim(args) .. ' '

  local result = {}
  local i = 1

  while i < string.len(args) do
    i = string.find(args, '%S', i) --[[@as integer]]

    local quote
    if string.byte(args, i) == string.byte("'") then
      quote = "'"
    elseif string.byte(args, i) == string.byte('"') then
      quote = '"'
    end

    if quote then
      local next_i = string.find(args, quote, i + 1, true)
      if not next_i then
        table.insert(result, string.sub(args, i + 1))
        return result
      end
      table.insert(result, string.sub(args, i + 1, next_i - 1))
      i = next_i + 2
    else
      local next_i = string.find(args, '%s', i)
      table.insert(result, string.sub(args, i, next_i - 1))
      i = next_i + 1
    end
  end

  return result
end

return M
