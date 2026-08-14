local dap = require('dap')
local dap_widgets = require('dap.ui.widgets')
local common = require('common')

vim.fn.sign_define('DapBreakpoint', { text = 'B', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapBreakpointCondition', { text = 'C', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapLogPoint', { text = 'L', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapStopped', { text = '', texthl = '', linehl = 'DiffAdd', numhl = '' })
vim.fn.sign_define('DapBreakpointRejected', { text = 'R', texthl = 'Character', linehl = '', numhl = '' })

vim.keymap.set('n', '<Leader><PageDown>', function()
  dap.continue()
end)

vim.keymap.set('n', '<Leader><Delete>', function()
  dap.terminate()
end)

vim.keymap.set('n', '<Leader><End>', function()
  dap.toggle_breakpoint()
end)

vim.keymap.set('n', common.ctrl_f9(), function()
  dap.clear_breakpoints()
end)

---@param buf integer
local set_keymap = function(buf)
  vim.keymap.set('n', '<Leader><Left>', function()
    dap.step_out()
  end, { buf = buf })

  vim.keymap.set('n', '<Leader><Right>', function()
    dap.step_into()
  end, { buf = buf })

  vim.keymap.set('n', '<Leader><Up>', function()
    dap.restart_frame()
  end, { buf = buf })

  vim.keymap.set('n', '<Leader><Down>', function()
    dap.step_over()
  end, { buf = buf })

  vim.keymap.set('n', '<Leader>k', function()
    dap_widgets.hover()
  end, { buf = buf })

  vim.keymap.set('n', '<Leader>.', function()
    dap_widgets.preview()
  end, { buf = buf })
end

---@param buf integer
local del_keymap = function(buf)
  vim.keymap.del('n', '<Leader><Left>', { buf = buf })
  vim.keymap.del('n', '<Leader><Right>', { buf = buf })
  vim.keymap.del('n', '<Leader><Up>', { buf = buf })
  vim.keymap.del('n', '<Leader><Down>', { buf = buf })
  vim.keymap.del('n', '<Leader>k', { buf = buf })
  vim.keymap.del('n', '<Leader>.', { buf = buf })
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
      set_keymap(args.buf)
    end,
  })

  valid_buffers(session.filetype):each(set_keymap)

  vim.api.nvim_create_user_command('DapSidebar', function()
    dap_widgets.sidebar(dap_widgets.scopes).open()
  end, {})

  session.on_close['dotfiles'] = function()
    vim.api.nvim_del_user_command('DapSidebar')
    vim.api.nvim_del_autocmd(id)
    valid_buffers(session.filetype):each(del_keymap)
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

local last_path = ''

dap.configurations.cpp = {
  {
    type = 'lldb',
    request = 'launch',
    name = 'Launch executable',
    program = function()
      return coroutine.create(function(co)
        vim.ui.input({ prompt = 'Path: ', completion = 'file', default = last_path }, function(path)
          last_path = path
          coroutine.resume(co, path)
        end)
      end)
    end,
  },
  {
    type = 'lldb',
    request = 'launch',
    name = 'Launch executable with args',
    program = function()
      return coroutine.create(function(co)
        vim.ui.input({ prompt = 'Path: ', completion = 'file', default = last_path }, function(path)
          last_path = path
          coroutine.resume(co, path)
        end)
      end)
    end,
    args = function()
      return coroutine.create(function(co)
        vim.ui.input({ prompt = 'Arguments: ' }, function(input)
          coroutine.resume(co, common.parse_args(input))
        end)
      end)
    end,
  },
}

dap.adapters.lldb = {
  type = 'executable',
  command = 'lldb-dap',
}

dap.configurations.python = {
  {
    type = 'debugpy',
    request = 'launch',
    name = 'Launch file',
    program = '${file}',
  },
  {
    type = 'debugpy',
    request = 'launch',
    name = 'Launch file with arguments',
    program = '${file}',
    args = function()
      return coroutine.create(function(co)
        vim.ui.input({ prompt = 'Arguments: ' }, function(input)
          coroutine.resume(co, common.parse_args(input))
        end)
      end)
    end,
  },
}

dap.adapters.debugpy = {
  type = 'executable',
  command = 'debugpy-adapter',
}
