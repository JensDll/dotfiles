return {
  {
    'nvim-treesitter/nvim-treesitter',
    branch = 'main',
    lazy = false,
    build = ':TSUpdate',
    config = function()
      require('nvim-treesitter').install({ 'javascript', 'typescript', 'bash', 'cpp', 'python' })
    end,
  },
}
