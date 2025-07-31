#!/bin/bash
# Run homelab documentation tool

cd "/home/zach/homelab-documentation"
source "homelab-env/bin/activate"

# Check for GUI support
if grep -qi microsoft /proc/version; then
    if [ -d "/mnt/wslg" ]; then
        export DISPLAY=:0
    else
        export DISPLAY=:0.0
    fi
fi

python homelab-wizard.py "$@"
