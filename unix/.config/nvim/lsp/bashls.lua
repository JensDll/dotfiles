---@type vim.lsp.Config
return {
  cmd = { 'bash-language-server', 'start' },
  settings = {
    bashIde = {
      -- https://github.com/bash-lsp/bash-language-server/blob/main/server/src/config.ts
      -- This is https://github.com/mrmlnc/fast-glob syntax
      globPattern = '*@(.sh|.inc|.bash|.command)',
    },
  },
  filetypes = { 'bash', 'sh' },
  root_markers = { '.git' },
}
