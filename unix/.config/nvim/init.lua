local common = require('common')

vim.g.mapleader = ' '
vim.g.maplocalleader = '\\'

vim.g.c_syntax_for_h = true

vim.o.number = true

vim.o.termguicolors = true

vim.o.list = true
vim.opt.listchars = { tab = '» ', trail = '·', nbsp = '␣' }

vim.o.ignorecase = true
vim.o.smartcase = true

vim.o.cursorline = true

vim.o.confirm = true

vim.o.mouse = 'a'

vim.o.undofile = true

vim.o.timeoutlen = 800

vim.o.foldmethod = 'expr'
vim.o.foldexpr = 'v:lua.vim.treesitter.foldexpr()'
vim.o.foldlevel = vim.o.foldnestmax

vim.cmd([[
  aunmenu PopUp.How-to\ disable\ mouse
  aunmenu PopUp.-2-
]])

vim.keymap.set('n', '<Esc>', '<Cmd>nohlsearch<CR>')

vim.keymap.set({ 'n', 'x', 'i' }, '<C-s>', '<Cmd>write<CR>', { desc = 'Save changes' })

if common.is_linux() then
  vim.keymap.set('c', '<C-s>', [[execute "silent write !pkexec tee '%:p'" | :edit!]], {
    desc = 'Save changes not owned by the current user',
  })
end

vim.keymap.set('n', '<Leader>q', '<Cmd>quit<CR>', { desc = ':quit' })

vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

vim.keymap.set('n', '<Leader>c', function()
  vim.ui.input({ completion = 'shellcmd', prompt = '$ ' }, function(command)
    if not command or command == '' then
      return
    end
    local id = vim.api.nvim_create_buf(false, true)
    vim.bo[id].bufhidden = 'wipe'
    vim.api.nvim_open_win(id, false, { win = 0, split = 'right' })
    vim.api.nvim_buf_set_lines(id, 0, -1, false, vim.fn.systemlist(command))
  end)
end, { desc = 'Execute the typed command and display its output in a new buffer' })

vim.keymap.set({ 'n', 'x' }, '<C-/>', function()
  return require('vim._comment').operator()
end, { expr = true })

vim.keymap.set('i', '<C-/>', function()
  return '<Esc>' .. require('vim._comment').operator() .. '_i'
end, { expr = true })

vim.keymap.set('o', '<C-/>', function()
  require('vim._comment').textobject()
end)

vim.keymap.set('x', '<C-c>', '"+y', {
  desc = 'Yank to clipboard register',
})

vim.keymap.set('x', '<C-x>', '"+d', {
  desc = 'Delete to clipboard register',
})

vim.keymap.set('n', '<Tab><Left>', '<Cmd>bprevious<CR>', {
  desc = 'Go to previous buffer',
})

vim.keymap.set('n', '<Tab><Right>', '<Cmd>bnext<CR>', {
  desc = 'Go to next buffer',
})

vim.keymap.set('n', '<Tab><Down>', '<Cmd>bdelete<CR>', {
  desc = 'Delete the current buffer',
})

vim.api.nvim_create_autocmd('TextYankPost', {
  desc = 'Highlight when yanking text',
  group = common.augroup,
  callback = function()
    vim.hl.on_yank({ timeout = 300 })
  end,
})

vim.api.nvim_create_autocmd('LspAttach', {
  desc = 'Enable LSP folding when available',
  group = common.augroup,
  callback = function(args)
    local client = vim.lsp.get_client_by_id(args.data.client_id)
    if client and client:supports_method(vim.lsp.protocol.Methods.textDocument_foldingRange) then
      local win = vim.api.nvim_get_current_win()
      vim.wo[win][0].foldexpr = 'v:lua.vim.lsp.foldexpr()'
    end
  end,
})

local parser_map = setmetatable({
  ['sh'] = 'bash',
}, {
  __index = function(_, key)
    return key
  end,
})

vim.api.nvim_create_autocmd('FileType', {
  desc = 'Enable treesitter highlighting when parser is available',
  group = common.augroup,
  callback = function(args)
    local name = parser_map[args.match]
    if vim.treesitter.language.add(name) then
      vim.treesitter.start(args.buf, name)
    end
  end,
})

vim.diagnostic.config({
  float = {
    source = true,
  },
})

vim.keymap.set('n', '<A-s>', '<Plug>(nvim.lsp.ctrl-s)', { desc = 'Cycle next signature' })
vim.api.nvim_create_autocmd('LspAttach', {
  callback = function(args)
    vim.keymap.set({ 'n', 'i' }, '<A-s>', function()
      vim.lsp.buf.signature_help()
    end, {
      buffer = args.buf,
      desc = 'Show signature information about the symbol under the cursor',
    })
  end,
})

vim.keymap.set('n', '<Leader>d', function()
  vim.diagnostic.open_float()
end, { desc = 'Show diagnostics for the current line' })

vim.keymap.set('n', '<Leader>a', function()
  vim.lsp.buf.code_action()
end, { desc = 'Show code actions' })

vim.keymap.set('n', '<Leader>f', function()
  vim.lsp.buf.format()
end, { desc = 'Show code actions' })

vim.keymap.set('n', '<F2>', function()
  vim.lsp.buf.rename()
end, { desc = 'Rename symbol under the cursor' })

vim.keymap.set('n', '<F12>', function()
  vim.lsp.buf.definition()
end, { desc = 'Go to definition' })

vim.keymap.set('n', common.shift_f12(), function()
  vim.lsp.buf.references()
end, { desc = 'Show references' })

vim.keymap.set('n', common.ctrl_shift_f12(), function()
  vim.lsp.buf.type_definition()
end, { desc = 'Go to type definition' })

vim.keymap.set('n', '<F4>', function()
  vim.lsp.buf.document_symbol()
end, { desc = 'Show document symbols' })

local github_src = function(name)
  return 'https://github.com/' .. name
end

vim.api.nvim_create_autocmd('PackChanged', {
  desc = 'Act on various vim.pack events',
  group = common.augroup,
  callback = function(args)
    if args.data.spec.name == 'nvim-treesitter' and args.data.kind == 'update' then
      vim.api.nvim_cmd({ cmd = 'TSUpdate' }, {})
    end
  end,
})

vim.pack.add({
  { src = github_src('catppuccin/nvim'), name = 'catppuccin' },
  { src = github_src('stevearc/conform.nvim') },
  { src = github_src('Saghen/blink.cmp'), version = vim.version.range('1.x') },
  { src = github_src('nvim-mini/mini.nvim') },
  { src = github_src('nvim-treesitter/nvim-treesitter') },
  { src = github_src('akinsho/bufferline.nvim') },
  { src = github_src('mfussenegger/nvim-dap') },
})

require('catppuccin').setup({
  no_italic = true,
  no_bold = true,
  no_underline = true,
})

vim.api.nvim_cmd({
  cmd = 'colorscheme',
  args = { 'catppuccin-nvim' },
}, {})

vim.api.nvim_create_user_command('FormatDisable', function(args)
  if args.bang then
    vim.b.disable_autoformat = true
  else
    vim.g.disable_autoformat = true
  end
end, {
  desc = 'Disable autoformat-on-save',
  bang = true,
})

vim.api.nvim_create_user_command('FormatEnable', function()
  vim.b.disable_autoformat = false
  vim.g.disable_autoformat = false
end, {
  desc = 'Re-enable autoformat-on-save',
})

require('conform').setup({
  formatters_by_ft = {
    lua = { 'stylua' },
    cmake = { 'gersemi' },
    c = { 'clang-format' },
    cpp = { 'clang-format' },
    javascript = { 'deno_fmt' },
    typescript = { 'deno_fmt' },
    json = { 'deno_fmt' },
    sh = { 'shfmt' },
    bash = { 'shfmt' },
    python = { 'ruff_fix', 'ruff_format' },
    xml = { 'yq_xml' },
  },
  default_format_opts = {
    lsp_format = 'fallback',
  },
  formatters = {
    ['yq_xml'] = {
      command = 'yq',
      args = { '--input-format', 'xml', '--output-format', 'xml', '-P' },
    },
  },
  format_on_save = function(id)
    if vim.g.disable_autoformat or vim.b[id].disable_autoformat then
      return nil
    end
    return { timeout_ms = 500 }
  end,
  notify_no_formatters = false,
})

require('blink.cmp').setup({
  keymap = {
    preset = 'super-tab',
  },
  appearance = {
    nerd_font_variant = 'mono',
  },
  completion = {
    documentation = {
      auto_show = false,
    },
    trigger = {
      show_in_snippet = false,
    },
    menu = {
      auto_show = false,
    },
  },
  sources = {
    default = { 'lsp', 'path', 'buffer' },
  },
  fuzzy = {
    implementation = 'prefer_rust_with_warning',
  },
  cmdline = {
    enabled = false,
  },
})

vim.keymap.set({ 'n', 'i', 'v' }, '<C-`>', function()
  if not MiniFiles.close() then
    MiniFiles.open()
  end
end, { desc = 'Toggle file explorer' })

vim.api.nvim_create_autocmd('User', {
  pattern = 'MiniFilesBufferCreate',
  group = common.augroup,
  desc = 'Cursor keymaps for mini.files',
  callback = function(args)
    local buf_id = args.data.buf_id

    local go_in = function()
      for _ = 1, vim.v.count1 do
        MiniFiles.go_in()
      end
    end

    local go_in_plus = function()
      for _ = 1, vim.v.count1 do
        MiniFiles.go_in({ close_on_file = true })
      end
    end

    local go_out = function()
      for _ = 1, vim.v.count1 do
        MiniFiles.go_out()
      end
    end

    local go_out_plus = function()
      go_out()
      MiniFiles.trim_right()
    end

    vim.keymap.set('n', '<Right>', go_in, { buffer = buf_id })
    vim.keymap.set('n', '<S-Right>', go_in_plus, { buffer = buf_id })
    vim.keymap.set('n', '<Left>', go_out, { buffer = buf_id })
    vim.keymap.set('n', '<S-Left>', go_out_plus, { buffer = buf_id })
  end,
})

require('mini.icons').setup()

require('mini.files').setup({
  options = {
    permanent_delete = false,
  },
  mappings = {
    show_help = '',
  },
})

require('bufferline').setup({
  options = {
    get_element_icon = function(element)
      local icon, hl = MiniIcons.get('filetype', element.filetype)
      return icon, hl
    end,
    show_buffer_close_icons = false,
  },
})

vim.fn.sign_define('DapBreakpoint', { text = 'B', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapBreakpointCondition', { text = 'C', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapLogPoint', { text = 'L', texthl = 'Character', linehl = '', numhl = '' })
vim.fn.sign_define('DapStopped', { text = '', texthl = '', linehl = 'DiffAdd', numhl = '' })
vim.fn.sign_define('DapBreakpointRejected', { text = 'R', texthl = 'Character', linehl = '', numhl = '' })

local dap = require('dap')

vim.keymap.set('n', '<F5>', function()
  dap.continue()
end)

vim.keymap.set('n', '<F9>', function()
  dap.toggle_breakpoint()
end)

vim.keymap.set('n', common.ctrl_f5(), function()
  dap.terminate()
end)

dap.listeners.after['event_initialized']['dotfiles'] = function()
  vim.keymap.set('n', '<C-Left>', function()
    dap.step_out()
  end)
  vim.keymap.set('n', '<C-Right>', function()
    dap.step_into()
  end)
  vim.keymap.set('n', '<C-Up>', function()
    dap.restart_frame()
  end)
  vim.keymap.set('n', '<C-Down>', function()
    dap.step_over()
  end)
  vim.keymap.set('n', '<2-LeftMouse>', function()
    require('dap.ui.widgets').preview()
  end)
end

dap.listeners.after['event_terminated']['dotfiles'] = function()
  vim.keymap.del('n', '<C-Left>')
  vim.keymap.del('n', '<C-Right>')
  vim.keymap.del('n', '<C-Up>')
  vim.keymap.del('n', '<C-Down>')
  vim.keymap.del('n', '<2-LeftMouse>')
end

require('pses').setup({
  settings = {
    CodeFormatting = {
      Preset = 'OTBS',
    },
  },
})

vim.lsp.enable({ 'luals', 'clangd', 'python', 'deno', 'csharp' })
