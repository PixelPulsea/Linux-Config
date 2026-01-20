--vim.opt options--
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.tabstop = 4
vim.opt.softtabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true

--keymaps--
vim.keymap.set('n', '<C-l>', '<C-w>h', { desc = 'Move windows'})

--require--
require("config.lazy")
