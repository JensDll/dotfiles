---@type vim.lsp.Config
return {
  cmd = { 'pylsp' },
  filetypes = { 'python' },
  root_markers = {
    'pyproject.toml',
    'setup.py',
    'setup.cfg',
    'requirements.txt',
    'Pipfile',
    '.git',
  },
  settings = {
    pylsp = {
      plugins = {
        autopep8 = {
          enabled = false,
        },
        pycodestyle = {
          enabled = false,
        },
        yapf = {
          enabled = false,
        },
      },
    },
  },
}
