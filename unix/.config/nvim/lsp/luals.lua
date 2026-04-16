local common = require('common')

local packages = vim.pack.get()

---@type vim.lsp.Config
return {
  cmd = { 'lua-language-server' },
  filetypes = { 'lua' },
  root_markers = {
    {
      '.luarc.json',
      '.luarc.jsonc',
    },
    'stylua.toml',
    '.git',
  },
  settings = {
    Lua = {},
  },
  on_init = function(client)
    if client.workspace_folders then
      local path = client.workspace_folders[1].name
      if path ~= common.config_path then
        return
      end
    end

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
    }
  end,
}
