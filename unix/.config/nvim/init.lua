require("plugins")

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
    -- https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd
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

vim.o.relativenumber = true

vim.keymap.set("n", "<leader>f", ":Format<CR>", { silent = true, unique = true })
vim.keymap.set("n", "<leader>F", ":FormatWrite<CR>", { silent = true, unique = true })
