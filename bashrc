#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
export HYPRSHOT_DIR="/home/me/Pictures/Screenshots"

alias vi="nvim"
alias vim="nvim"
alias finance='java -cp "/home/me/Documents/Java/Personal/PersonalFinance" PersonalFinance';

export EDITOR="nvim"
export VISUAL="nvim"

cowsay -f stegosaurus Try typing "finance"
echo
PS1=' > '

eval $(luarocks path --bin)
