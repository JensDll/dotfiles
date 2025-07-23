vim.g.mapleader = ' '
vim.g.maplocalleader = '\\'

vim.o.number = true

vim.o.termguicolors = true

vim.o.list = true
vim.opt.listchars = { tab = '» ', trail = '·', nbsp = '␣' }

vim.o.ignorecase = true
vim.o.smartcase = true

vim.o.cursorline = true

vim.o.confirm = true

vim.o.mouse = 'a'

vim.o.undofile = true

vim.o.timeoutlen = 800

vim.schedule(function()
  vim.o.clipboard = 'unnamedplus'
end)

vim.api.nvim_cmd({
  cmd = 'aunmenu',
  args = { 'PopUp.How-to\\ disable\\ mouse' },
}, {})

vim.api.nvim_cmd({
  cmd = 'aunmenu',
  args = { 'PopUp.-2-' },
}, {})

require('config.keymap')
require('config.autocmd')
require('config.lazy')
require('config.lsp')
