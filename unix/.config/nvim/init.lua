vim.o.relativenumber = true

vim.env.PATH = vim.env.PATH .. ":" .. vim.fn.expand("$HOME/.local/bin")

vim.lsp.enable('luals')

require("config.lazy")