vim.api.nvim_create_autocmd('FileType', {
  group = DOTFILES_AUGROUP,
  callback = function(args)
    if vim.treesitter.language.add(args.match) then
      vim.treesitter.start(args.buf, args.match)
    end
  end,
})

return {
  'nvim-treesitter/nvim-treesitter',
  branch = 'master',
  lazy = false,
  build = ':TSUpdate',
  opts = {
    highlight = {
      enable = true,
    },
  },
}
