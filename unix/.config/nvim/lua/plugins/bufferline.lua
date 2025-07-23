return {
  {
    'akinsho/bufferline.nvim',
    event = 'VeryLazy',
    keys = {
      { '<Leader>bp', '<Cmd>BufferLineTogglePin<CR>', desc = 'Toggle Pin' },
    },
    ---@type bufferline.UserConfig
    opts = {
      options = {
        get_element_icon = function(element)
          local icon, hl = MiniIcons.get('filetype', element.filetype)
          return icon, hl
        end,
        show_buffer_close_icons = false,
      },
    },
  },
}
