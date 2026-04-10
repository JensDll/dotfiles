local hex_to_char = function(x)
  return string.char(tonumber(x, 16))
end

---@param url string | nil
---@return string | nil
local urldecode = function(url)
  if url == nil then
    return
  end
  url = url:gsub('+', ' ')
  url = url:gsub('%%(%x%x)', hex_to_char)
  return url
end

local get_or_create_buf = function(name)
  local buffers = vim.api.nvim_list_bufs()

  for _, buf in pairs(buffers) do
    local bufname = vim.api.nvim_buf_get_name(buf)
    if string.find(name, '^/%$metadata%$/.*$') then
      local normalized_bufname = string.gsub(bufname, '\\', '/')
      if string.find(normalized_bufname, name) then
        return buf
      end
    else
      if bufname == name then
        return buf
      elseif string.find(string.gsub(bufname, '%u:\\', '/'), name) then
        return buf
      end
    end
  end

  local bufnr = vim.api.nvim_create_buf(true, true)

  vim.api.nvim_buf_set_name(bufnr, name)

  return bufnr
end

-- vim.api.nvim_create_autocmd('BufReadCmd', {
--   pattern = { 'csharp:/*' },
--   callback = function(args)
--     local client = vim.lsp.get_clients({ name = 'csharp' })[1]
--     local uri = urldecode(args.file)
--
--     local params = {
--       timeout = 5000,
--       textDocument = {
--         uri = uri,
--       },
--     }
--
--     local result, err = client:request_sync('csharp/metadata', params, 10000, 0)
--
--     if not err and result ~= nil then
--       local lines = vim.split(result.result.source, '\r\n')
--       local bufnr = get_or_create_buf(uri)
--       vim.api.nvim_buf_set_name(bufnr, args.file)
--       vim.api.nvim_set_option_value('modifiable', true, { buf = bufnr })
--       vim.api.nvim_set_option_value('readonly', false, { buf = bufnr })
--       vim.api.nvim_buf_set_lines(bufnr, 0, -1, true, lines)
--       vim.api.nvim_set_option_value('modifiable', false, { buf = bufnr })
--       vim.api.nvim_set_option_value('readonly', true, { buf = bufnr })
--       vim.api.nvim_set_option_value('filetype', 'cs', { buf = bufnr })
--       vim.api.nvim_set_option_value('modified', false, { buf = bufnr })
--       vim.lsp.buf_attach_client(bufnr, client.id)
--     end
--   end,
-- })

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
  root_markers = { '.root' },
  get_language_id = function(_, filetype)
    if filetype == 'cs' then
      return 'csharp'
    end
    return filetype
  end,
}
