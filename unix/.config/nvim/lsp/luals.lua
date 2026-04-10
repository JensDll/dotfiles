local packages = vim.pack.get()

---@type vim.lsp.Config
return {
  cmd = { 'lua-language-server' },
  filetypes = { 'lua' },
  root_markers = {
    '.luarc.json',
    '.luarc.jsonc',
    '.luacheckrc',
    '.stylua.toml',
    'stylua.toml',
    'selene.toml',
    'selene.yml',
    '.git',
  },
  settings = {
    Lua = {},
  },
  on_init = function(client)
    local library = {
      vim.env.VIMRUNTIME,
    }

    for _, value in ipairs(packages) do
      table.insert(library, value.path)
    end

    client.config.settings.Lua = {
      runtime = {
        version = 'LuaJIT',
        path = { 'lua/?.lua', 'lua/?/init.lua' },
      },
      workspace = {
        library = library,
      },
      -- diagnostics = {
      --   groupSeverity = {
      --     ['type-check'] = 'Hint',
      --   },
      -- },
    }
  end,
}
