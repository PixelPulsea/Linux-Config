-- bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- Load plugins
require("lazy").setup(require("plugins"), {
    rocks = { enabled = false },
    change_detection = { notify = false },
})

-- Then set your theme
vim.cmd("colorscheme tokyonight")

-- Treesitter config
-- Set a writable parser install directory
local parser_install_dir = vim.fn.stdpath("data") .. "/treesitter"

require("nvim-treesitter.configs").setup {
    ensure_installed = { "c", "cpp", "java" },
    highlight = { enable = true },
    parser_install_dir = parser_install_dir,
}

local map = vim.keymap.set
-- Disable arrows in Normal, Insert, and Visual modes
map({'n', 'i', 'v'}, '<Left>',  '<Nop>')
map({'n', 'i', 'v'}, '<Right>', '<Nop>')
map({'n', 'i', 'v'}, '<Up>',    '<Nop>')
map({'n', 'i', 'v'}, '<Down>',  '<Nop>')

-- === Your options and keymaps go here ===
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.smartindent = true
vim.opt.number = true
vim.opt.relativenumber = true
vim.o.hlsearch = false

-- Run current C++/Java file
vim.keymap.set("n", "<C-A-n>", function()
  local file = vim.fn.expand("%:p")
  local dir  = vim.fn.expand("%:p:h")
  local name = vim.fn.expand("%:t")
  local base = vim.fn.expand("%:t:r")
  local ext  = vim.fn.expand("%:e")
  vim.cmd("write")

  if ext == "java" then
    vim.cmd("botright split | terminal bash -lc 'cd "
      .. vim.fn.fnameescape(dir) ..
      " && javac " .. vim.fn.fnameescape(name) ..
      " && java " .. base ..
      " ; read -p \"Press Enter to exit\"'")
  elseif ext == "cpp" then
    vim.cmd("botright split | terminal bash -lc 'cd "
      .. vim.fn.fnameescape(dir) ..
      " && g++ -std=c++17 " .. vim.fn.fnameescape(name) ..
      " -o " .. base ..
      " && ./" .. base ..
      " ; read -p \"Press Enter to exit\"'")
  else
    print("No run command for this filetype")
  end
end, { noremap = true, silent = true })

-- Clipboard copy
vim.api.nvim_set_keymap('v', '<C-c>', ':w !wl-copy<CR><CR>', { noremap = true, silent = true })
vim.api.nvim_set_keymap('n', '<C-c>', ':%w !wl-copy<CR><CR>', { noremap = true, silent = true })

