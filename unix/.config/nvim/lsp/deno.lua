---@type vim.lsp.Config
return {
  cmd = { 'deno', 'lsp' },
  filetypes = { 'javascript', 'typescript' },
  root_markers = {
    'deno.json',
    'deno.jsonc',
    '.git',
  },
  settings = {
    deno = {
      enable = true,
    },
  },
}
