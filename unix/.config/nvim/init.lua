vim.g.mapleader = ' '
vim.g.maplocalleader = '\\'
vim.g.have_nerd_font = true

vim.o.relativenumber = true
vim.o.termguicolors = true

vim.schedule(function()
  vim.o.clipboard = 'unnamedplus'
end)

vim.env.PATH = vim.env.PATH .. ':' .. vim.fn.expand('$HOME/.local/bin')

vim.keymap.set('n', '<Esc>', '<Cmd>nohlsearch<CR>')
vim.keymap.set('n', '<Leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostic quickfix list' })
vim.keymap.set({ 'n', 'i', 'v' }, '<C-s>', '<Cmd>write<CR><Esc>', { desc = 'Save changes and escape' })
vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

require('config.lazy')

vim.lsp.enable('luals')
