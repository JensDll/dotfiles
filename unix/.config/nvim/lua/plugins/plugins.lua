return {
  {
    'mason-org/mason.nvim',
    opts = {},
  },
  {
    'stevearc/conform.nvim',
    event = 'BufWritePre',
    cmd = 'ConformInfo',
    keys = {
      {
        '<leader>f',
        function()
          require('conform').format({ async = true })
        end,
        desc = 'Format the buffer',
      },
    },
    ---@type conform.setupOpts
    opts = {
      formatters_by_ft = {
        lua = { 'stylua' },
        cmake = { 'cmake_format' },
        cpp = { 'clang-format' },
        hpp = { 'clang-format' },
        javascript = { 'prettier' },
        typescript = { 'prettier' },
        yaml = { 'prettier' },
        json = { 'prettier' },
        sh = { 'shfmt' },
      },
      default_format_opts = {
        lsp_format = 'never',
      },
      format_on_save = {
        timeout_ms = 500,
      },
    },
  },
  {
    'akinsho/bufferline.nvim',
    event = 'VeryLazy',
    ---@type bufferline.UserConfig
    opts = {
      options = {
        get_element_icon = function(element)
          local icon, hl = MiniIcons.get('filetype', element.filetype)
          return icon, hl
        end,
      },
    },
  },
  {
    'saghen/blink.cmp',
    dependencies = { 'rafamadriz/friendly-snippets' },
    version = '1.*',
    ---@type blink.cmp.Config
    opts = {
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
      },
      sources = {
        default = { 'lsp', 'path', 'snippets', 'buffer' },
      },
      fuzzy = {
        implementation = 'prefer_rust_with_warning',
      },
      cmdline = {
        enabled = false,
      },
    },
    opts_extend = { 'sources.default' },
  },
  {
    'lewis6991/gitsigns.nvim',
    event = 'VeryLazy',
    opts = {},
  },
  {
    'nvim-treesitter/nvim-treesitter',
    branch = 'main',
    lazy = false,
    build = ':TSUpdate',
    config = function()
      require('nvim-treesitter').install({ 'javascript', 'typescript', 'bash', 'cpp' })
    end,
  },
}
