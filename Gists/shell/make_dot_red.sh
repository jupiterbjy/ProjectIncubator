#!/bin/bash

# copy .bashrc & .bash_logout first
# https://superuser.com/a/268703/1252755
cp /etc/skel/.bash* ~

# Append the new PS1 setting to .bashrc
echo 'export PS1="\[\e[31m\]\u@\h\[\e[00m\]:\[\e[01;34m\]\w\[\e[00m\]\$ "' >> ~/.bashrc

# Reload the .bashrc to apply changes
source ~/.bashrc
