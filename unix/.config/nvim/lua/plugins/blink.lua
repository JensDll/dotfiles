return {
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
}
