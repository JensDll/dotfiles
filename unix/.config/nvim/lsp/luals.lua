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
  on_init = function(client)
    if client.workspace_folders then
      local path = client.workspace_folders[1].name
      if
        path ~= vim.fn.stdpath('config')
        and (vim.uv.fs_stat(path .. '/.luarc.json') or vim.uv.fs_stat(path .. '/.luarc.jsonc'))
      then
        return
      end
    end

    local library = { vim.env.VIMRUNTIME, '${3rd}/luv/library' }

    local lazy_root = require('lazy.core.config').options.root

    local req, err = vim.uv.fs_scandir(lazy_root)

    if err then
      vim.api.nvim_echo({
        { 'Not configuring Lua Language Server\n', 'WarningMsg' },
        { err, 'WarningMsg' },
      }, true, {})
      return
    end

    local function iter()
      return vim.uv.fs_scandir_next(req)
    end

    for name, file_type in iter do
      if file_type == 'directory' then
        table.insert(library, lazy_root .. '/' .. name)
      end
    end

    -- https://luals.github.io/wiki/settings
    client.config.settings.Lua = vim.tbl_deep_extend('force', client.config.settings.Lua, {
      runtime = {
        version = 'LuaJIT',
        path = {
          'lua/?.lua',
          'lua/?/init.lua',
        },
      },
      workspace = {
        checkThirdParty = 'Disable',
        library = library,
      },
    })
  end,
  settings = {
    Lua = {},
  },
}
