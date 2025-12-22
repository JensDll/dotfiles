return {
  'akinsho/bufferline.nvim',
  event = 'VeryLazy',
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
}
