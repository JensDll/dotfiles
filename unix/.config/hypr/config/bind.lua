local ctrl = function(...)
  return table.concat({ 'CTRL', ... }, '+')
end

local super = function(...)
  return table.concat({ 'SUPER', ... }, '+')
end

local super_shift = function(...)
  return table.concat({ 'SUPER', 'SHIFT', ... }, '+')
end

hl.bind(super('return'), hl.dsp.exec_cmd('ghostty'))
hl.bind(super('f'), hl.dsp.exec_cmd('firefox'))
hl.bind(super('d'), hl.dsp.exec_cmd('firefox --new-window ~/Documents'))
hl.bind(super('c'), hl.dsp.exec_cmd('chromium'))
hl.bind(super('q'), hl.dsp.window.close())

for i = 1, 10 do
  local key = i % 10
  hl.bind(super(key), hl.dsp.focus({ workspace = i }))
  hl.bind(super_shift(key), hl.dsp.window.move({ workspace = i }))
end

hl.bind(super('left'), hl.dsp.focus({ workspace = 'e-1' }))
hl.bind(super('right'), hl.dsp.focus({ workspace = 'e+1' }))

hl.bind(ctrl('left'), hl.dsp.focus({ direction = 'left' }))
hl.bind(ctrl('right'), hl.dsp.focus({ direction = 'right' }))
hl.bind(ctrl('up'), hl.dsp.focus({ direction = 'up' }))
hl.bind(ctrl('down'), hl.dsp.focus({ direction = 'down' }))

hl.bind(super('mouse:272'), hl.dsp.window.drag(), { mouse = true })
hl.bind(super('mouse:273'), hl.dsp.window.resize(), { mouse = true })
