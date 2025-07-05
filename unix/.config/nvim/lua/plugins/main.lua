return {
  {
    'mason-org/mason.nvim',
    opts = {},
  },
  {
    'nvim-lua/plenary.nvim',
    lazy = true,
  },
  {
    'nvim-tree/nvim-web-devicons',
    lazy = true,
  },
  {
    'MunifTanjim/nui.nvim',
    lazy = true,
  },
  {
    'stevearc/conform.nvim',
    event = { 'BufWritePre' },
    cmd = { 'ConformInfo' },
    keys = {
      {
        '<leader>f',
        function()
          require('conform').format({ async = true })
        end,
        desc = 'Format the buffer',
      },
    },
    ---@module "conform"
    ---@type conform.setupOpts
    opts = {
      formatters_by_ft = {
        lua = { 'stylua' },
      },
      default_format_opts = {
        lsp_format = 'never',
      },
      format_on_save = {
        timeout_ms = 500,
      },
    },
  },
  -- {
  --   "nvim-neo-tree/neo-tree.nvim",
  --   lazy = false,
  --   branch = "v3.x",
  --   opts = {
  --     filesystem = {
  --       filtered_items = {
  --         visible = true,
  --       },
  --       follow_current_file = {
  --         enabled = true,
  --         leave_dirs_open = true,
  --       },
  --     },
  --   },
  --   keys = {
  --     {
  --       "<C-b>",
  --       function()
  --         require("neo-tree.command").execute({
  --           action = "show",
  --           toggle = true,
  --         })
  --       end,
  --       desc = "Toggle neo-tree",
  --       mode = { "n", "i", "v" },
  --     },
  --   },
  -- },
  {
    'akinsho/bufferline.nvim',
    event = { 'VeryLazy' },
    opts = {},
  },
  {
    'stevearc/oil.nvim',
    command = { 'Oil' },
    ---@module 'oil'
    ---@type oil.SetupOpts
    opts = {
      view_options = {
        show_hidden = true,
      },
      keymaps = {
        ['<C-b>'] = { 'actions.close', mode = 'n' },
        ['<2-LeftMouse>'] = { 'actions.select' },
      },
    },
    keys = {
      { '<C-b>', '<Cmd>Oil<CR>', mode = { 'n', 'i', 'v' } },
    },
  },
  {
    'saghen/blink.cmp',
    dependencies = { 'rafamadriz/friendly-snippets' },
    version = '1.*',
    ---@module 'blink.cmp'
    ---@type blink.cmp.Config
    opts = {
      keymap = { preset = 'super-tab' },
      appearance = {
        nerd_font_variant = 'mono',
      },
      completion = { documentation = { auto_show = false } },
      sources = {
        default = { 'lsp', 'path', 'snippets', 'buffer' },
      },
      fuzzy = { implementation = 'prefer_rust_with_warning' },
      cmdline = {
        keymap = { preset = 'inherit' },
        completion = { menu = { auto_show = true } },
      },
    },
    opts_extend = { 'sources.default' },
  },
}
