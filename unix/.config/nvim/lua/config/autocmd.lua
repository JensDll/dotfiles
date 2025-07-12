DOTFILES_AUGROUP = vim.api.nvim_create_augroup('dotfiles', {})

vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking text',
  group = DOTFILES_AUGROUP,
  callback = function()
    vim.hl.on_yank({ timeout = 300 })
  end,
})
