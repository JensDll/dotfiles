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
          statusline.SEPARATION,
          statusline.DIAGNOSTIC,
          '  ',
          statusline.FILEINFO,
          '  ',
          statusline.PROGRESS,
        },
      })
    end,
  },
}
