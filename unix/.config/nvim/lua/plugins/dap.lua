vim.fn.sign_define('DapBreakpoint', { text = 'B', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapBreakpointCondition', { text = 'C', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapLogPoint', { text = 'L', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapStopped', { text = '', texthl = '', linehl = 'DiffAdd', numhl = '' })
vim.fn.sign_define('DapBreakpointRejected', { text = 'R', texthl = 'Character', linehl = '', numhl = '' })

---@type LazyPluginSpec
return {
  'mfussenegger/nvim-dap',
  keys = {
    {
      '<F5>',
      function()
        require('dap').continue()
      end,
    },
    {
      '<F29>',
      function()
        require('dap').terminate()
      end,
    },
    {
      '<Leader>b',
      function()
        require('dap').toggle_breakpoint()
      end,
    },
  },
  config = function()
    local dap = require('dap')

    dap.adapters.lldb = {
      type = 'executable',
      command = 'lldb-dap-20',
    }

    local prev_path

    dap.configurations.cpp = {
      {
        name = 'Launch',
        request = 'launch',
        type = 'lldb',
        program = function()
          prev_path = vim.fn.input({
            prompt = 'Path to executable: ',
            default = prev_path,
            completion = 'file',
          })
          return prev_path
        end,
        cwd = '${workspaceFolder}',
      },
    }

    dap.configurations.c = dap.configurations.cpp

    dap.listeners.after['event_initialized']['dotfiles'] = function(_, _)
      vim.keymap.set('n', '<C-Left>', function()
        require('dap').step_out()
      end)
      vim.keymap.set('n', '<C-Right>', function()
        require('dap').step_into()
      end)
      vim.keymap.set('n', '<C-Up>', function()
        require('dap').restart_frame()
      end)
      vim.keymap.set('n', '<C-Down>', function()
        require('dap').step_over()
      end)
      vim.keymap.set('n', '<2-LeftMouse>', function()
        require('dap.ui.widgets').preview()
      end)
    end

    dap.listeners.after['event_terminated']['dotfiles'] = function(_, _)
      vim.keymap.del('n', '<C-Left>')
      vim.keymap.del('n', '<C-Right>')
      vim.keymap.del('n', '<C-Up>')
      vim.keymap.del('n', '<C-Down>')
      vim.keymap.del('n', '<2-LeftMouse>')
    end
  end,
}
