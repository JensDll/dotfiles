local datapath = vim.fn.stdpath("data")

local lazypath = datapath .. "/lazy/lazy.nvim"

if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "--branch=stable",
    "https://github.com/folke/lazy.nvim.git",
    lazypath,
  })
end

vim.opt.runtimepath:prepend(lazypath)

vim.g.mapleader = " "

require("lazy").setup({
  "editorconfig/editorconfig-vim",
  "mhartington/formatter.nvim",
  {
    "VonHeikemen/lsp-zero.nvim",
    branch = "dev-v3",
    dependencies = {
      { "neovim/nvim-lspconfig" },
      {
        "williamboman/mason.nvim",
        build = function()
          pcall(vim.cmd, "MasonUpdate")
        end,
      },
      { "williamboman/mason-lspconfig.nvim" },
      { "hrsh7th/nvim-cmp" },
      { "hrsh7th/cmp-nvim-lsp" },
      { "L3MON4D3/LuaSnip" },
    },
  },
})

vim.o.relativenumber = true

local lsp = require("lsp-zero").preset({})

lsp.on_attach(function(client, bufnr)
  lsp.default_keymaps({ buffer = bufnr })
end)

lsp.extend_cmp()

require("mason").setup()

require("formatter").setup({
  logging = true,
  log_level = vim.log.levels.WARN,
  filetype = {
    sh = {
      function()
        local shiftwidth = vim.opt.shiftwidth:get()
        local expandtab = vim.opt.expandtab:get()

        if not expandtab then
          shiftwidth = 0
        end

        return {
          exe = "shfmt",
          args = { "--indent", shiftwidth, "--binary-next-line", "--space-redirects", "--keep-padding" },
          stdin = true,
        }
      end,
    },
  },
})
