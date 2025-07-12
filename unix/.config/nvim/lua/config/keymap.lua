vim.keymap.set('n', '<Esc>', '<Cmd>nohlsearch<CR>')

vim.keymap.set('n', '<Leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostic quickfix list' })

vim.keymap.set({ 'n', 'v', 'i' }, '<C-s>', '<Cmd>write<CR>', { desc = 'Save changes' })

vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

vim.keymap.set('n', '<Leader>c', function()
  vim.ui.input({ completion = 'shellcmd', prompt = '$ ' }, function(command)
    if not command or command == '' then
      return
    end
    local id = vim.api.nvim_create_buf(false, true)
    vim.bo[id].bufhidden = 'wipe'
    vim.api.nvim_open_win(id, false, { win = 0, split = 'right' })
    vim.api.nvim_buf_set_lines(id, 0, -1, false, vim.fn.systemlist(command))
  end)
end, { desc = 'Execute the typed command and display its output in a new buffer' })

vim.keymap.set('n', '<Leader>d', function()
  vim.diagnostic.open_float()
end, { desc = 'Show diagnostics for the current line' })

vim.keymap.set('n', '<A-s>', '<Plug>(nvim.lsp.ctrl-s)')

vim.api.nvim_create_autocmd('LspAttach', {
  callback = function(args)
    vim.keymap.set({ 'n', 'i', 's' }, '<A-s>', function()
      vim.lsp.buf.signature_help()
    end, { buffer = args.buf })
  end,
})
