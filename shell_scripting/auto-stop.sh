#!/bin/bash

# Check 1: Is VS Code active?
VSCODE_ACTIVE=0
if ps aux | grep -E "vscode-server|node" | grep -v grep > /dev/null; then
    VSCODE_ACTIVE=1
fi

# Check 2: Is any standard SSH terminal open?
SSH_ACTIVE=0
if ps aux | grep "sshd:" | grep -v grep > /dev/null; then
    SSH_ACTIVE=1
fi

# Shut down ONLY if both are completely idle (0)
if [ $VSCODE_ACTIVE -eq 0 ] && [ $SSH_ACTIVE -eq 0 ]; then
    /sbin/shutdown -h now
fi
