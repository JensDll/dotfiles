local conf = require('pses.config')

local M = {}

---@class pses.session
---@field status string
---@field languageServiceTransport? string
---@field languageServicePipeName? string
---@field debugServiceTransport? string
---@field debugServicePipeName? string
---@field powerShellVersion string

---@param callback fun(session?: pses.session, err?: string): nil
local function wait_for_session(callback)
  local poll = assert(vim.uv.new_fs_poll())
  poll:start(conf.config.pses.session_path, 100, function(err)
    poll:stop()
    poll:close()
    if err then
      callback(nil, err)
      return
    end
    local file, open_err = io.open(conf.config.pses.session_path)
    if not file then
      callback(nil, open_err)
      return
    end
    local session = file:read('*a')
    file:close()
    callback(vim.json.decode(session))
  end)

  local timer = assert(vim.uv.new_timer())
  timer:start(5000, 0, function()
    timer:stop()
    timer:close()
    if poll:is_active() then
      poll:stop()
      poll:close()
      vim.schedule(function()
        vim.notify(
          string.format(
            "[pses] Failed to start. Poll on '%s' timed out after 5 seconds.",
            conf.config.pses.session_path
          ),
          vim.log.levels.WARN
        )
      end)
    end
  end)
end

---@param command string[]
---@param buf integer
local function start_pses(command, buf)
  local console_buf = vim.api.nvim_create_buf(true, false)

  vim.uv.fs_open(conf.config.pses.session_path, vim.uv.constants.O_CREAT, tonumber('644', 8))

  vim.api.nvim_buf_call(console_buf, function()
    local term_channel = vim.fn.jobstart(command, { term = true })
    print('term: ', term_channel)
  end)

  wait_for_session(function(session, err)
    vim.schedule(function()
      if err then
        vim.notify(string.format('[pses] %s', err), vim.log.levels.ERROR)
        return
      end
      local client_id = vim.lsp.start({
        name = 'pses',
        cmd = vim.lsp.rpc.connect(session.languageServicePipeName),
        root_dir = vim.fs.root(buf, conf.config.root_markers),
      }, { bufnr = buf })
      print('client: ', client_id)
    end)
  end)
end

---@param user_config pses.user_config?
function M.setup(user_config)
  if vim.fn.executable('pwsh') == 0 then
    return
  end

  conf.config = vim.tbl_deep_extend('keep', user_config or {}, conf.default_config)

  vim.validate('pses.path', conf.config.pses.path, 'string')
  vim.validate('pses.log_level', conf.config.pses.log_level, 'string')
  vim.validate('pses.log_path', conf.config.pses.log_path, 'string', true)
  vim.validate('pses.session_path', conf.config.pses.session_path, 'string')

  local command = {
    'pwsh',
    '-NoLogo',
    '-NonInteractive',
    '-NoProfile',
    '-File',
    vim.fs.joinpath(conf.config.pses.path, 'PowerShellEditorServices', 'Start-EditorServices.ps1'),
    '-HostName',
    'nvim',
    '-HostProfileId',
    'Neovim',
    '-BundledModulesPath',
    conf.config.pses.path,
    '-LogLevel',
    conf.config.pses.log_level,
    '-LanguageServiceOnly',
    '-SessionDetailsPath',
    conf.config.pses.session_path,
    '-EnableConsoleRepl',
  }

  if conf.config.pses.log_path then
    table.insert(command, '-LogPath')
    table.insert(command, conf.config.pses.log_path)
  end

  vim.api.nvim_create_autocmd('FileType', {
    desc = 'PowerShell editor services',
    pattern = 'ps1',
    group = conf.augroup,
    callback = function(args)
      start_pses(command, args.buf)
    end,
  })
end

return M
