vim.keymap.set('n', '<Esc>', '<Cmd>nohlsearch<CR>')

vim.keymap.set({ 'n', 'x', 'i' }, '<C-s>', '<Cmd>write<CR>', { desc = 'Save changes' })

vim.keymap.set('c', '<C-s>', [[execute "silent write !pkexec tee '%:p'" | :edit!]], {
  desc = "Save changes to the file it's not owned by the current user",
})

vim.keymap.set('n', '<Leader>q', '<Cmd>quit<CR>', { desc = ':quit' })

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

vim.keymap.set({ 'n', 'x' }, '<C-/>', function()
  return require('vim._comment').operator()
end, { expr = true })

vim.keymap.set('i', '<C-/>', function()
  return '<Esc>' .. require('vim._comment').operator() .. '_i'
end, { expr = true })

vim.keymap.set('o', '<C-/>', function()
  require('vim._comment').textobject()
end)

vim.keymap.set('x', '<C-c>', 'y', {
  desc = 'Visual mode yank',
})

vim.keymap.set('n', '<Tab><Right>', '<Cmd>bnext<CR>', {
  desc = 'Go to next buffer',
})

vim.keymap.set('n', '<Tab><Left>', '<Cmd>bprevious<CR>', {
  desc = 'Go to previous buffer',
})
