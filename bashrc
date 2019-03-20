# add homebrew to path
[[ -d $HOME/.homebrew/bin ]] && export PATH=$HOME/.homebrew/bin:$PATH

# ignore common commands in history
export HISTIGNORE="&:ls:[bf]g:exit:reset:clear:cd *";

# history max size
export HISTSIZE=4096;

# ignore dupes from history file
export HISTCONTROL="ignoreboth:erasedups"

# allow for history substitution
shopt -s histreedit;

# save multiline commands as one line
shopt -s cmdhist

# autocorrect minor spelling errors
shopt -s dirspell 2>/dev/null

# auto fix errors in `cd` command
shopt -s cdspell 2>/dev/null

# check windows size if windows is resized
shopt -s checkwinsize 2>/dev/null

# use extra globing features. See man bash, search extglob.
shopt -s extglob 2>/dev/null

# include .files when globbing.
shopt -s dotglob 2>/dev/null

# language
export LC_ALL="en_GB.UTF-8"
export LANG="en_GB.UTF-8"

# completion
bind "set completion-ignore-case on"
bind "set completion-map-case on"
bind "set show-all-if-ambiguous on"

# colours
alias "ls=ls -G"
export GREP_OPTIONS='--color=auto'
export GREP_COLOR="1;32"
export MANPAGER="less -X"

# homebrew
export HOMEBREW_NO_ANALYTICS=1
export HOMEBREW_AUTO_UPDATE_SECS=3600
export HOMEBREW_CASK_OPTS="--appdir=$HOME/Applications"

# bash completion
if [ -f $(brew --prefix)/etc/bash_completion ]; then
  source $(brew --prefix)/etc/bash_completion
fi
