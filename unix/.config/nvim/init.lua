vim.g.mapleader = ' '
vim.g.maplocalleader = '\\'

vim.o.number = true

vim.o.termguicolors = true

vim.o.list = true
vim.opt.listchars = { tab = '» ', trail = '·', nbsp = '␣' }

vim.o.ignorecase = true
vim.o.smartcase = true

vim.o.cursorline = true

vim.o.scrolloff = 10

vim.o.confirm = true

vim.o.mouse = 'a'

vim.o.undofile = true

vim.o.timeoutlen = 800

vim.schedule(function()
  vim.o.clipboard = 'unnamedplus'
end)

vim.env.PATH = vim.env.PATH .. ':' .. vim.fn.expand('$HOME/.local/bin')

vim.o.foldenable = false
vim.o.foldmethod = 'expr'
vim.o.foldexpr = 'v:lua.vim.treesitter.foldexpr()'

require('config.keymap')
require('config.autocmd')
require('config.lazy')

vim.diagnostic.config({
  float = {
    source = true,
  },
})

vim.lsp.enable({ 'luals', 'clangd' })
