local repo = 'https://github.com/folke/lazy.nvim'
local path = vim.fn.stdpath('data') .. '/lazy/lazy.nvim'

if not vim.uv.fs_stat(path) then
  local result = vim.system({ 'git', 'clone', '--filter=blob:none', '--branch=v11.17.1', repo, path }):wait()
  if result.code ~= 0 then
    vim.api.nvim_echo({
      { 'Failed to clone ' .. repo .. '\n', 'WarningMsg' },
      { result.stderr, 'WarningMsg' },
    }, true, {})
    return
  end
end

vim.opt.rtp:prepend(path)

require('lazy').setup({
  spec = {
    { import = 'plugins' },
  },
  install = {
    missing = false,
    colorscheme = {},
  },
  change_detection = {
    enabled = false,
  },
  rocks = {
    enabled = false,
  },
  dev = {
    path = vim.fn.stdpath('config') .. '/lazy',
  },
})
