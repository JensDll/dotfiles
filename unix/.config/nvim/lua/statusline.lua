---@class statusline.opts
---@field line? (string | integer)[]
---@field diagnostic? statusline.config.diagnostic[]

---@class statusline.config
---@field line (string | integer)[]
---@field diagnostic statusline.config.diagnostic[]

---@class statusline.config.diagnostic
---@field hl string
---@field sign string

local M = {
  SEPARATION = 1,
  FILEICON = 2,
  FILENAME = 3,
  FILEINFO = 4,
  DIAGNOSTIC = 5,
  PROGRESS = 6,
  TRUNCATION = 7,
}

---@type statusline.config
local config

local function win_buf_id()
  return vim.api.nvim_win_get_buf(vim.g.statusline_winid)
end

local function win_is_active()
  return tonumber(vim.g.statusline_winid or -1) == vim.api.nvim_get_current_win()
end

local segments = {
  function()
    return '%='
  end,
  function()
    local filetype = vim.api.nvim_get_option_value('filetype', { buf = win_buf_id() })
    local icon, hl = MiniIcons.get('filetype', filetype)
    if win_is_active() then
      return string.format('%%#%s#%s%%* ', hl, icon)
    end
    return icon
  end,
  function()
    return '%f %h%w%m%r'
  end,
  function()
    return '%20.(%l,%c  %L Lines%)'
  end,
  function()
    local active = win_is_active()
    return vim
      .iter(pairs(vim.diagnostic.count(win_buf_id())))
      :map(function(severity, count)
        local entry = config.diagnostic[severity]
        if active then
          return string.format('%%#%s#%s:%u%%*', entry.hl, entry.sign, count)
        end
        return string.format('%s:%u', entry.sign, count)
      end)
      :join(' ')
  end,
  function()
    return '%P'
  end,
  function()
    return '%<'
  end,
}

function M.render()
  return vim
    .iter(ipairs(config.line))
    :map(function(_, value)
      if type(value) == 'string' then
        return value
      end
      return segments[value]()
    end)
    :join('')
end

---@param opts? statusline.opts
function M.setup(opts)
  config = vim.tbl_deep_extend('keep', opts or {}, {
    line = {
      M.FILENAME,
      M.TRUNCATION,
      M.SEPARATION,
      M.DIAGNOSTIC,
      ' ',
      M.FILEINFO,
      '  ',
      M.PROGRESS,
    },
    diagnostic = {
      [vim.diagnostic.severity.ERROR] = { hl = 'DiagnosticSignError', sign = 'E' },
      [vim.diagnostic.severity.WARN] = { hl = 'DiagnosticSignWarn', sign = 'W' },
      [vim.diagnostic.severity.INFO] = { hl = 'DiagnosticSignInfo', sign = 'I' },
      [vim.diagnostic.severity.HINT] = { hl = 'DiagnosticSignHint', sign = 'H' },
    },
  }) --[[@as statusline.config]]
  vim.o.statusline = "%!v:lua.require'statusline'.render()"
end

return M
