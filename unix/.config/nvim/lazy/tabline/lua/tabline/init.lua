local M = {}

local tabline_count = 0

function M.tabline()
  tabline_count = tabline_count + 1
  print('tabline', tabline_count)
  local ids = vim.tbl_filter(function(id)
    return vim.api.nvim_buf_is_loaded(id) and vim.bo[id].buflisted
  end, vim.api.nvim_list_bufs())

  local line = ''

  local current_id = vim.api.nvim_get_current_buf()

  for i = 1, #ids do
    local id = ids[i]

    local name = vim.api.nvim_buf_get_name(id)

    if id == current_id then
      line = line .. '%#TabLineSel#'
    else
      line = line .. '%#TabLine#'
    end

    line = line .. '%' .. id .. "@v:lua.require'tabline'.handle_click@" .. vim.fs.basename(name) .. '%X'
  end

  line = line .. '%#TabLineFill#'

  return line
end

local count = 0

function M.handle_click(id, num_clicks, button, modifiers)
  count = count + 1
  print('click', count)
  if button == 'l' then
    vim.api.nvim_set_current_buf(id)
    -- vim.api.nvim_set_current_win(0)
  elseif button == 'r' then
    vim.api.nvim_buf_delete(id, {})
  end
end

function M.setup(opts)
  -- vim.o.tabline = "%!v:lua.require'tabline'.tabline()"
end

return M
