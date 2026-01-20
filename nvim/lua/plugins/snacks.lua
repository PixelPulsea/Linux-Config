return {
  "folke/snacks.nvim",
  priority = 1000,
  lazy = false,
  ---@type snacks.Config
  opts = {
    bigfile = { enabled = true },
    explorer = { 
        enabled = true,
        replace_netrw = true,
    },
    input = { enabled = true },
    picker = { enabled = true },
    notifier = { enabled = true },
    quickfile = { enabled = true },
    scroll = { enabled = true },
    },
    keys = {
        { "<leader>ff", function() Snacks.picker.files() end, desc = "Smart Find Files" },
        { "<leader>fe", function() Snacks.explorer() end, desc = "Explorer" },
        { "<leader>fc", function() Snacks.picker.files({ cwd = vim.fn.stdpath("config") }) end, desc = "Find Config File" },
        { "<leader>fn", function() Snacks.picker.notifications() end, desc = "Notification History" },
    },
}
