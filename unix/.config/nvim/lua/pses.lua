local M = {}

---@class pses.opts
---@field path? string
---@field root_markers? string[]
---@field log_level? 'Trace'|'Debug'|'Information'|'Warning'|'Error'|'Critical'|'None'
---@field log_path? string
---@field settings? pses.settings

---@class pses.settings
---@field EnableProfileLoading? boolean
---@field Cwd? string
---@field EnableReferencesCodeLens? boolean
---@field AnalyzeOpenDocumentsOnly? boolean
---@field ScriptAnalysis? pses.settings.script_analysis
---@field CodeFormatting? pses.settings.code_formatting
---@field CodeFolding? pses.settings.code_folding
---@field Pester? pses.settings.pester

---@class pses.settings.script_analysis
---@field Enable? boolean
---@field SettingsPath? string

---@class pses.settings.code_formatting
---@field AddWhitespaceAroundPipe? boolean
---@field AutoCorrectAliases? boolean
---@field AvoidSemicolonsAsLineTerminators? boolean
---@field UseConstantStrings? boolean
---@field Preset? 'Custom'|'Allman'|'OTBS'|'Stroustrup'
---@field OpenBraceOnSameLine? boolean
---@field NewLineAfterOpenBrace? boolean
---@field NewLineAfterCloseBrace? boolean
---@field PipelineIndentationStyle? 'IncreaseIndentationForFirstPipeline'|'IncreaseIndentationAfterEveryPipeline'|'NoIndentation'|'None'
---@field TrimWhitespaceAroundPipe? boolean
---@field WhitespaceBeforeOpenBrace? boolean
---@field WhitespaceBeforeOpenParen? boolean
---@field WhitespaceAroundOperator? boolean
---@field WhitespaceAfterSeparator? boolean
---@field WhitespaceBetweenParameters? boolean
---@field WhitespaceInsideBrace? boolean
---@field IgnoreOneLineBlock? boolean
---@field AlignPropertyValuePairs? boolean
---@field AlignEnumMemberValues? boolean
---@field UseCorrectCasing? boolean

---@class pses.settings.code_folding
---@field Enable? boolean
---@field ShowLastLine? boolean

---@class pses.settings.pester
---@field CodeLens? boolean
---@field UseLegacyCodeLens? boolean

---@class pses.config
---@field path string
---@field root_markers string[]
---@field log_level 'Trace'|'Debug'|'Information'|'Warning'|'Error'|'Critical'|'None'
---@field log_path? string
---@field settings? pses.settings

---@class pses.session
---@field status string
---@field languageServiceTransport? string
---@field languageServicePipeName? string
---@field debugServiceTransport? string
---@field debugServicePipeName? string
---@field powerShellVersion string

---@type pses.config
local config
local augroup = vim.api.nvim_create_augroup('pses', {})

---@param path string
---@param callback fun(err?: string, session?: pses.session): nil
local wait_for_session = function(path, callback)
  local callback_after_unlink = function(err, session)
    vim.uv.fs_unlink(path, function(unlink_err)
      callback(err or unlink_err, session)
    end)
  end

  local poll = assert(vim.uv.new_fs_poll())
  poll:start(path, 100, function(err)
    poll:stop()
    poll:close()
    if err then
      callback_after_unlink(err)
      return
    end
    local file, open_err = io.open(path)
    if not file then
      callback_after_unlink(open_err)
      return
    end
    local session = file:read('*a')
    file:close()
    callback_after_unlink(nil, vim.json.decode(session))
  end)

  local timer = assert(vim.uv.new_timer())
  timer:start(5000, 0, function()
    timer:stop()
    timer:close()
    if poll:is_active() then
      poll:stop()
      poll:close()
      callback_after_unlink(string.format("Failed to start. Poll on '%s' timed out after 5 seconds.", path))
    end
  end)
end

---@param root_dir? string
local find_pses_client = function(root_dir)
  for _, client in ipairs(vim.lsp.get_clients({ name = 'pses' })) do
    if client.root_dir == root_dir then
      return client
    end
  end
end

---@param command string[]
---@param buf integer
local start_or_attach_pses = function(command, buf)
  local root_dir = vim.fs.root(buf, config.root_markers)

  local client = find_pses_client(root_dir)
  if client then
    vim.lsp.buf_attach_client(buf, client.id)
    return
  end

  vim.uv.fs_open(command[8], vim.uv.constants.O_CREAT, tonumber('600', 8), function(open_err)
    if open_err then
      vim.schedule(function()
        vim.notify(string.format('[pses] %s', open_err), vim.log.levels.ERROR)
      end)
      return
    end

    vim.system(command)

    wait_for_session(command[8], function(session_err, session)
      vim.schedule(function()
        if session_err then
          vim.notify(string.format('[pses] %s', session_err), vim.log.levels.ERROR)
          return
        end

        vim.lsp.start({
          name = 'pses',
          cmd = vim.lsp.rpc.connect(session.languageServicePipeName),
          root_dir = root_dir,
          settings = { powershell = config.settings },
        }, { bufnr = buf })
      end)
    end)
  end)
end

---@param args string
---@return string[]
local parse_args = function(args)
  args = vim.fn.trim(args) .. ' '

  local result = {}
  local i = 1

  while i < string.len(args) do
    i = string.find(args, '%S', i) --[[@as integer]]

    local quote
    if string.byte(args, i) == string.byte("'") then
      quote = "'"
    elseif string.byte(args, i) == string.byte('"') then
      quote = '"'
    end

    if quote then
      local next_i = string.find(args, quote, i + 1, true)
      if not next_i then
        table.insert(result, string.sub(args, i) .. quote)
        return result
      end
      table.insert(result, string.sub(args, i, next_i))
      i = next_i + 2
    else
      local next_i = string.find(args, '%s', i)
      table.insert(result, string.sub(args, i, next_i - 1))
      i = next_i + 1
    end
  end

  return result
end

local setup_dap = function()
  local dap = require('dap')

  local session_path = os.tmpname()

  local command = {
    'pwsh',
    '-NoLogo',
    '-NonInteractive',
    '-NoProfile',
    '-File',
    vim.fs.joinpath(config.path, 'PowerShellEditorServices', 'Start-EditorServices.ps1'),
    '-SessionDetailsPath',
    session_path,
    '-HostName',
    'pses.nvim',
    '-HostProfileId',
    'pses.nvim',
    '-BundledModulesPath',
    config.path,
    '-LogLevel',
    config.log_level,
    '-EnableConsoleRepl',
    '-DebugServiceOnly',
  }

  dap.configurations.ps1 = {
    {
      type = 'pses',
      request = 'launch',
      name = 'Current file',
      script = '${file}',
    },
    {
      type = 'pses',
      request = 'launch',
      name = 'Current file with args',
      script = '${file}',
      args = function()
        return coroutine.create(function(co)
          vim.ui.input({ prompt = 'Arguments: ' }, function(input)
            coroutine.resume(co, parse_args(input))
          end)
        end)
      end,
    },
    {
      name = 'Attach to process',
      type = 'ps1',
      request = 'attach',
      processId = '${command:pickProcess}',
    },
  }

  ---@type integer?
  local console
  ---@type integer?
  local console_buf

  dap.adapters.pses = function(callback)
    if console_buf then
      return
    end

    console_buf = vim.api.nvim_create_buf(true, false)

    vim.uv.fs_open(session_path, vim.uv.constants.O_CREAT, tonumber('600', 8))

    vim.api.nvim_buf_call(console_buf, function()
      console = vim.fn.jobstart(command, { term = true })
    end)

    wait_for_session(session_path, function(err, session)
      vim.schedule(function()
        if err then
          vim.notify(string.format('[pses] %s', err), vim.log.levels.ERROR)
          return
        end
        callback({
          type = 'pipe',
          pipe = session.debugServicePipeName,
        })
      end)
    end)
  end

  dap.listeners.after['event_initialized']['pses'] = function(session)
    session.on_close['pses'] = function()
      if console_buf then
        vim.api.nvim_buf_delete(console_buf, { force = true })
      end
      console = nil
      console_buf = nil
    end
  end

  dap.listeners.after['event_powerShell/sendKeyPress']['pses'] = function()
    if console then
      vim.api.nvim_chan_send(console, 'p')
    end
  end
end

---@param opts? pses.opts
M.setup = function(opts)
  if vim.fn.executable('pwsh') == 0 then
    return
  end

  ---@diagnostic disable: need-check-nil
  vim.validate('opts.path', opts.path, 'string', true)
  vim.validate('opts.root_markers', opts.root_markers, 'table', true)
  vim.validate('opts.log_level', opts.log_level, 'string', true)
  vim.validate('opts.log_path', opts.log_path, 'string', true)
  vim.validate('opts.settings', opts.settings, 'table', true)
  ---@diagnostic disable: need-check-nil

  config = vim.tbl_deep_extend('keep', opts or {}, {
    path = vim.fs.joinpath(
      vim.env.XDG_DATA_HOME or vim.fs.joinpath(vim.env.HOME, '.local', 'share'),
      'PowerShellEditorServices'
    ),
    root_markers = { 'PSScriptAnalyzerSettings.psd1', '.git' },
    log_level = 'Warning',
  }) --[[@as pses.config]]

  local command = {
    'pwsh',
    '-NoLogo',
    '-NonInteractive',
    '-NoProfile',
    '-File',
    vim.fs.joinpath(config.path, 'PowerShellEditorServices', 'Start-EditorServices.ps1'),
    '-SessionDetailsPath',
    os.tmpname(),
    '-HostName',
    'pses.nvim',
    '-HostProfileId',
    'pses.nvim',
    '-BundledModulesPath',
    config.path,
    '-LogLevel',
    config.log_level,
    '-LanguageServiceOnly',
  }

  if config.log_path then
    table.insert(command, '-LogPath')
    table.insert(command, config.log_path)
  end

  if pcall(require, 'dap') then
    setup_dap()
  end

  vim.api.nvim_create_autocmd('FileType', {
    desc = 'PowerShell editor services',
    pattern = 'ps1',
    group = augroup,
    callback = function(args)
      start_or_attach_pses(command, args.buf)
    end,
  })
end

return M
