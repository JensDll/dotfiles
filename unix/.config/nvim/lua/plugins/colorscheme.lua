return {
  'catppuccin/nvim',
  name = 'catppuccin',
  lazy = false,
  priority = 1000,
  ---@type CatppuccinOptions
  opts = {
    no_italic = true,
    no_bold = true,
    no_underline = true,
  },
  init = function()
    vim.api.nvim_cmd({
      cmd = 'colorscheme',
      args = { 'catppuccin' },
    }, {})
  end,
}
