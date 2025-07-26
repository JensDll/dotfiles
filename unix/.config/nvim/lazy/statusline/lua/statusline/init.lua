local M = {
  SPACE = 1,
  SEPARATION = 2,
  FILEICON = 3,
  FILENAME = 4,
  FILEINFO = 5,
  DIAGNOSTIC = 6,
  PROGRESS = 7,
  TRUNCATION = 8,
}

local function win_buf_id()
  return vim.api.nvim_win_get_buf(vim.g.statusline_winid)
end

local segments = {
  function()
    return ' '
  end,
  function()
    return '%='
  end,
  function()
    local filetype = vim.api.nvim_get_option_value('filetype', { buf = win_buf_id() })
    local icon, hl = MiniIcons.get('filetype', filetype)
    return '%#' .. hl .. '#' .. icon .. '%*'
  end,
  function()
    return '%f %h%w%m%r'
  end,
  function()
    return '%L lines'
  end,
  function()
    local count = vim.diagnostic.count(win_buf_id())
    local warn_count, error_count = count[vim.diagnostic.severity.WARN] or 0, count[vim.diagnostic.severity.ERROR] or 0
    return '%#DiagnosticWarn#' .. warn_count .. ' W  %#DiagnosticError#' .. error_count .. ' E%*'
  end,
  function()
    return '%P'
  end,
  function()
    return '%<'
  end,
}

local config = {
  line = {
    M.TRUNCATION,
    M.FILENAME,
    M.SEPARATION,
    M.FILEINFO,
    M.SPACE,
    M.SPACE,
    M.PROGRESS,
  },
}

function M.render()
  local result = ''

  for _, index in ipairs(config.line) do
    result = result .. segments[index]()
  end

  return result
end

function M.setup(opts)
  config = vim.tbl_deep_extend('force', config, opts)
  vim.o.statusline = "%!v:lua.require'statusline'.render()"
end

return M
