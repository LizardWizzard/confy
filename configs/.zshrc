# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

source $HOME/.zsh/completion.zsh
# Lines configured by zsh-newuser-install
# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
# zstyle :compinstall filename '$HOME/.zshrc'

# Initialize the completion system
autoload -Uz compinit

# Cache completion if nothing changed - faster startup time
typeset -i updated_at=$(date +'%j' -r ~/.zcompdump 2>/dev/null || stat -f '%Sm' -t '%j' ~/.zcompdump 2>/dev/null)
if [ $(date +'%j') != $updated_at ]; then
  compinit -i
else
  compinit -C -i
fi

# Enhanced form of menu completion called `menu selection'
zmodload -i zsh/complist

# setopt appendhistory autocd beep extendedglob nomatch notify

# https://unix.stackexchange.com/a/273863
# To prevent history from recording duplicated entries
# (such as ls -l entered many times during single shell session),
# you can set the hist_ignore_all_dups option:
setopt hist_ignore_all_dups

# A useful trick to prevent particular entries from being recorded
# into a history by preceding them with at least one space.
setopt hist_ignore_space

source $HOME/.zsh/powerlevel10k/powerlevel10k.zsh-theme
source $HOME/.zsh/fast-syntax-highlighting/F-Sy-H.plugin.zsh
source $HOME/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
source $HOME/.zsh/history.zsh
# source $HOME/.zsh/key-bindings.zsh
# source $HOME/.zsh/just.zsh

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

alias weather='curl v2.wttr.in'

export PATH="/home/dr/.local/bin:$PATH"
#export PATH="$HOME/.poetry/bin:$PATH"

export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

export PATH=$PATH:/usr/local/go/bin
export PATH=$PATH:/usr/share/bcc/tools

source "$HOME/.cargo/env"

alias g='git'
alias ga='git add'
alias gd='git diff'
alias gco='git checkout'
alias gst='git status'
alias glg='git log'
alias glgo='git log --oneline'
alias glgs='git log --stat'
alias gp='git push'
alias gpfl='git push --force-with-lease'
alias grbc='git rebase --continue'
alias grba='git rebase --abort'
alias gb='git branch'
alias gfp='git fetch --prune'
alias gcan='git commit -a --amend --no-edit'
alias gwip='git commit -am "WIP" --no-verify'
alias gunwip='git reset --soft HEAD~1; git restore --staged .'

alias kc='cargo check'
alias kba='cargo build --all'

alias ipy='ipython --no-confirm-exit --no-banner --quick'

alias newkey='ssh-keygen -t ed25519 -a 100 -f'

alias j='just'

alias ls='exa --all'
alias ll='exa -alF --all'

source /usr/share/fzf/shell/key-bindings.zsh
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

[ -f ~/.zshrc.local ] && source ~/.zshrc.local
