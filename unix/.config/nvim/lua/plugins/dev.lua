return {
  {
    'statusline',
    dev = true,
    config = function()
      local statusline = require('statusline')
      statusline.setup({
        line = {
          statusline.TRUNCATION,
          statusline.FILENAME,
          statusline.SEPARATION,
          statusline.DIAGNOSTIC,
          statusline.SPACE,
          statusline.SPACE,
          statusline.FILEINFO,
          statusline.SPACE,
          statusline.SPACE,
          statusline.PROGRESS,
        },
      })
    end,
  },
}
