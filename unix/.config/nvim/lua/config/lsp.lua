vim.diagnostic.config({
  float = {
    source = true,
  },
})

vim.keymap.set('n', '<A-s>', '<Plug>(nvim.lsp.ctrl-s)', { desc = 'Cycle next signature' })
vim.api.nvim_create_autocmd('LspAttach', {
  callback = function(args)
    vim.keymap.set({ 'n', 'i' }, '<A-s>', function()
      vim.lsp.buf.signature_help()
    end, {
      buffer = args.buf,
      desc = 'Show signature information about the symbol under the cursor',
    })
  end,
})

vim.keymap.set('n', '<Leader>d', function()
  vim.diagnostic.open_float()
end, { desc = 'Show diagnostics for the current line' })

vim.keymap.set('n', '<Leader>a', function()
  vim.lsp.buf.code_action()
end, { desc = 'Show code actions' })

vim.keymap.set('n', '<F2>', function()
  vim.lsp.buf.rename()
end, { desc = 'Rename symbol under the cursor' })

vim.keymap.set('n', '<F24>', function()
  vim.lsp.buf.references()
end, { desc = 'Show references' })

vim.keymap.set('n', '<F12>', function()
  vim.lsp.buf.definition()
end, { desc = 'Go to definition' })

vim.keymap.set('n', '<F36>', function()
  vim.lsp.buf.type_definition()
end, { desc = 'Go to type definition' })

vim.lsp.enable({ 'luals', 'clangd', 'bashls', 'tsls' })
