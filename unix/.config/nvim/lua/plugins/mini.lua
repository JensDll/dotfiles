vim.keymap.set({ 'n', 'i', 'v' }, '<C-b>', function()
  if not MiniFiles.close() then
    MiniFiles.open()
  end
end, { desc = 'Toggle file explorer' })

vim.api.nvim_create_autocmd('User', {
  pattern = 'MiniFilesBufferCreate',
  group = DOTFILES_AUGROUP,
  desc = 'Cursor keymaps for mini.files',
  callback = function(args)
    local buf_id = args.data.buf_id

    local go_in = function()
      for _ = 1, vim.v.count1 do
        MiniFiles.go_in()
      end
    end

    local go_in_plus = function()
      for _ = 1, vim.v.count1 do
        MiniFiles.go_in({ close_on_file = true })
      end
    end

    local go_out = function()
      for _ = 1, vim.v.count1 do
        MiniFiles.go_out()
      end
    end

    local go_out_plus = function()
      go_out()
      MiniFiles.trim_right()
    end

    vim.keymap.set('n', '<Right>', go_in, { buffer = buf_id })
    vim.keymap.set('n', '<S-Right>', go_in_plus, { buffer = buf_id })
    vim.keymap.set('n', '<Left>', go_out, { buffer = buf_id })
    vim.keymap.set('n', '<S-Left>', go_out_plus, { buffer = buf_id })
  end,
})

return {
  {
    'echasnovski/mini.nvim',
    init = function()
      require('mini.icons').setup()

      require('mini.files').setup({
        options = {
          permanent_delete = false,
        },
        mappings = {
          show_help = '',
        },
      })
    end,
  },
}
