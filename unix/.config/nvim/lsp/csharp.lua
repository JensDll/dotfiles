---@type vim.lsp.Config
return {
  cmd = function(dispatchers, config)
    return vim.lsp.rpc.start({ 'csharp-ls', '--features', 'metadata-uris' }, dispatchers, {
      cwd = config.cmd_cwd or config.root_dir,
      env = config.cmd_env,
      detached = config.detached,
    })
  end,
  filetypes = { 'cs' },
  root_markers = { '.root', '.git' },
  get_language_id = function(_, filetype)
    if filetype == 'cs' then
      return 'csharp'
    end
    return filetype
  end,
}
