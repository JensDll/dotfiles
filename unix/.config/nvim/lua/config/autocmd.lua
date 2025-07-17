DOTFILES_AUGROUP = vim.api.nvim_create_augroup('dotfiles', {})

vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking text',
  group = DOTFILES_AUGROUP,
  callback = function()
    vim.hl.on_yank({ timeout = 300 })
  end,
})

vim.o.foldmethod = 'expr'
vim.o.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
vim.o.foldlevel = vim.o.foldnestmax

vim.api.nvim_create_autocmd('LspAttach', {
  desc = 'Enable LSP folding when available',
  group = DOTFILES_AUGROUP,
  callback = function(args)
    local client = vim.lsp.get_client_by_id(args.data.client_id)
    if client and client:supports_method('textDocument/foldingRange') then
      local win = vim.api.nvim_get_current_win()
      vim.wo[win][0].foldexpr = 'v:lua.vim.lsp.foldexpr()'
    end
  end,
})

local parser_map = {
  ['sh'] = 'bash',
}

setmetatable(parser_map, {
  __index = function(_, key)
    return key
  end,
})

vim.api.nvim_create_autocmd('FileType', {
  desc = 'Enable treesitter highlighting when parser is available',
  group = DOTFILES_AUGROUP,
  callback = function(args)
    local name = parser_map[args.match]
    if vim.treesitter.language.add(name) then
      vim.treesitter.start(args.buf, name)
    end
  end,
})
