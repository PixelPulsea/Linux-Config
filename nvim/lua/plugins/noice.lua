-- lazy.nvim
return {
  "folke/noice.nvim",
  event = "VeryLazy",
  opts = {
      lsp = {
          progress = {
              enabled = false,
          },
      },

      messages = {
          enabled = true,
      }
  },
  dependencies = {
    "MunifTanjim/nui.nvim",
    "rcarriga/nvim-notify",
    }
}
