#!/bin/bash
# uso: CMD via stdin ; tools/shot.sh <pasta> <NN-nome> <espera> "<destaque>"...
P=$1; N=$2; W=$3; shift 3
ssh lnx06 'cat > /tmp/cmd.txt; printf "%s" "$(cat /tmp/cmd.txt)" > /tmp/cmd.txt; tmux send-keys -t demo clear Enter; sleep 1; tmux load-buffer /tmp/cmd.txt; tmux paste-buffer -t demo; tmux send-keys -t demo Enter'
sleep "$W"
ssh lnx06 "tmux capture-pane -p -t demo" > logs/$P/$N.screen.txt
ssh lnx06 "tmux capture-pane -p -S -200 -t demo" > logs/$P/$N.txt
grep . logs/$P/$N.screen.txt
"/c/Program Files/Oracle/VirtualBox/VBoxManage.exe" controlvm lnx06-eduardo screenshotpng "$(cygpath -w "$PWD/assets/$P/raw/$N.png")"
CW=11 CH=22 python tools/annotate.py assets/$P/raw/$N.png logs/$P/$N.screen.txt assets/$P/$N.png "$@"
