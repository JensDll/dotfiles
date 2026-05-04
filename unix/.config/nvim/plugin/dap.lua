local dap = require('dap')
local dap_widgets = require('dap.ui.widgets')
local common = require('common')

vim.fn.sign_define('DapBreakpoint', { text = 'B', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapBreakpointCondition', { text = 'C', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapLogPoint', { text = 'L', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapStopped', { text = '', texthl = '', linehl = 'DiffAdd', numhl = '' })
vim.fn.sign_define('DapBreakpointRejected', { text = 'R', texthl = 'Character', linehl = '', numhl = '' })

vim.keymap.set('n', '<F5>', function()
  dap.continue()
end)

vim.keymap.set('n', common.ctrl_f5(), function()
  dap.terminate()
end)

vim.keymap.set('n', '<F9>', function()
  dap.toggle_breakpoint()
end)

vim.keymap.set('n', common.ctrl_f9(), function()
  dap.clear_breakpoints()
end)

---@param buf integer
local set_dap_keymap = function(buf)
  vim.keymap.set('n', '<C-Left>', function()
    dap.step_out()
  end, { buf = buf })

  vim.keymap.set('n', '<C-Right>', function()
    dap.step_into()
  end, { buf = buf })

  vim.keymap.set('n', '<C-Up>', function()
    dap.restart_frame()
  end, { buf = buf })

  vim.keymap.set('n', '<C-Down>', function()
    dap.step_over()
  end, { buf = buf })

  vim.keymap.set('n', 'K', function()
    dap_widgets.hover()
  end, { buf = buf })
end

---@param buf integer
local del_dap_keymap = function(buf)
  vim.keymap.del('n', '<C-Left>', { buf = buf })
  vim.keymap.del('n', '<C-Right>', { buf = buf })
  vim.keymap.del('n', '<C-Up>', { buf = buf })
  vim.keymap.del('n', '<C-Down>', { buf = buf })
  vim.keymap.del('n', 'K', { buf = buf })
end

---@param filetype string
local valid_buffers = function(filetype)
  return vim
    .iter(ipairs(vim.fn.getbufinfo({ buflisted = 1 })))
    :map(function(_, buf)
      return buf.bufnr
    end)
    :filter(function(buf)
      return vim.bo[buf].filetype == filetype
    end)
    :filter(vim.api.nvim_buf_is_valid)
end

dap.listeners.after['event_initialized']['dotfiles'] = function(session)
  local id = vim.api.nvim_create_autocmd('FileType', {
    desc = 'Set debug keymaps on buffers with filetype of DAP session',
    pattern = session.filetype,
    group = common.augroup,
    callback = function(args)
      set_dap_keymap(args.buf)
    end,
  })

  valid_buffers(session.filetype):each(set_dap_keymap)

  vim.api.nvim_create_user_command('DapSidebar', function()
    dap_widgets.sidebar(dap_widgets.scopes).open()
  end, {})

  session.on_close['dotfiles'] = function()
    vim.api.nvim_del_user_command('DapSidebar')
    vim.api.nvim_del_autocmd(id)
    valid_buffers(session.filetype):each(del_dap_keymap)
  end
end

dap.configurations.cmake = {
  {
    type = 'cmake_preset',
    request = 'launch',
    name = 'Launch preset',
  },
}

dap.adapters.cmake_preset = function(callback)
  vim.ui.input({ prompt = 'Preset: ' }, function(preset)
    callback({
      type = 'pipe',
      pipe = '${pipe}',
      executable = {
        command = 'cmake',
        args = {
          '--preset',
          preset,
          '--debugger',
          '--debugger-pipe',
          '${pipe}',
        },
      },
    })
  end)
end
