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

vim.o.timeoutlen = 300

vim.schedule(function()
  vim.o.clipboard = 'unnamedplus'
end)

vim.env.PATH = vim.env.PATH .. ':' .. vim.fn.expand('$HOME/.local/bin')

vim.keymap.set('n', '<Esc>', '<Cmd>nohlsearch<CR>')
vim.keymap.set('n', '<Leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostic quickfix list' })
vim.keymap.set({ 'n', 'v' }, '<C-s>', '<Cmd>write<CR>', { desc = 'Save changes' })
vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking (copying) text',
  group = vim.api.nvim_create_augroup('config', { clear = true }),
  callback = function()
    vim.hl.on_yank({ timeout = 300 })
  end,
})

require('config.lazy')

vim.lsp.enable('luals')
