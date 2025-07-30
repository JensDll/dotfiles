local function echo(...)
  vim.api.nvim_echo({ { 'Lua Language Server\n', 'WarningMsg' }, ... }, true, {})
end

local function append_lazy_paths(paths)
  if not package.loaded['lazy'] then
    return
  end

  local root = require('lazy.core.config').options.root
  local dir, error = vim.uv.fs_scandir(root)

  if not dir then
    echo({ 'Not configuring lazy.nvim paths\n', 'WarningMsg' }, { error, 'WarningMsg' })
    return
  end

  local function iter()
    return vim.uv.fs_scandir_next(dir)
  end

  for name, file_type in iter do
    if file_type == 'directory' then
      table.insert(paths, root .. '/' .. name)
    end
  end
end

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

    local paths = { vim.env.VIMRUNTIME, '${3rd}/luv/library' }
    append_lazy_paths(paths)

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
        library = paths,
      },
    })
  end,
  settings = {
    Lua = {},
  },
}
