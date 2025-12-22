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
  commands = {
    ['deno.cache'] = function(cmd, ctx)
      print('deno.cache command')
    end,
    ['deno.showReferences'] = function(cmd, ctx)
      print('deno.showReferences command')
    end,
  },
}
