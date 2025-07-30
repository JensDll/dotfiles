vim.api.nvim_create_user_command('FormatDisable', function(args)
  if args.bang then
    vim.b.disable_autoformat = true
  else
    vim.g.disable_autoformat = true
  end
end, {
  desc = 'Disable autoformat-on-save',
  bang = true,
})

vim.api.nvim_create_user_command('FormatEnable', function()
  vim.b.disable_autoformat = false
  vim.g.disable_autoformat = false
end, {
  desc = 'Re-enable autoformat-on-save',
})

return {
  'stevearc/conform.nvim',
  event = 'BufWritePre',
  cmd = 'ConformInfo',
  keys = {
    {
      '<leader>f',
      function()
        require('conform').format({ async = true })
      end,
      desc = 'Format the buffer',
    },
  },
  ---@type conform.setupOpts
  opts = {
    formatters_by_ft = {
      lua = { 'stylua' },
      cmake = { 'gersemi' },
      c = { 'clang-format' },
      cpp = { 'clang-format' },
      javascript = { 'prettier' },
      typescript = { 'prettier' },
      sh = { 'shfmt' },
      bash = { 'shfmt' },
      python = { 'isort', 'black' },
    },
    default_format_opts = {
      lsp_format = 'never',
    },
    format_on_save = function(id)
      if not vim.g.disable_autoformat and not vim.b[id].disable_autoformat then
        return { timeout_ms = 500 }
      end
    end,
    notify_no_formatters = false,
  },
}
