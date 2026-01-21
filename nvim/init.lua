--vim.opt options--
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.tabstop = 4
vim.opt.softtabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true

--keymaps--
vim.keymap.set('n', '<C-l>', '<C-w>h', { desc = 'Move windows'})
vim.keymap.set({ 'n', 'v', 'x' }, '<Up>', '<nop>')
vim.keymap.set({ 'n', 'v', 'x' }, '<Down>', '<nop>')
vim.keymap.set({ 'n', 'v', 'x' }, '<Left>', '<nop>')
vim.keymap.set({ 'n', 'v', 'x' }, '<Right>', '<nop>')
vim.keymap.set('i', '<Up>', '<nop>')
vim.keymap.set('i', '<Down>', '<nop>')
vim.keymap.set('i', '<Left>', '<nop>')
vim.keymap.set('i', '<Right>', '<nop>')

--require--
require("config.lazy")
