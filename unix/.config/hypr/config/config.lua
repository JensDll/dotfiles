hl.monitor({
  output = 'DP-1',
  mode = '2560x1440@144',
  position = 'auto',
  scale = '1',
})

hl.config({
  general = {
    gaps_in = 0,
    gaps_out = 0,
    border_size = 0,
  },
  decoration = {
    shadow = {
      enabled = false,
    },
  },
  input = {
    kb_layout = 'gb',
    sensitivity = -0.7,
  },
  animations = {
    enabled = false,
  },
  misc = {
    disable_hyprland_logo = true,
  },
})
