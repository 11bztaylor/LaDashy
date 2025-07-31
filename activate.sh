#!/bin/bash
# Activate homelab documentation environment

cd "/home/zach/homelab-documentation"
source "homelab-env/bin/activate"
echo -e "\033[0;32mHomelab environment activated!\033[0m"
echo "Run: python homelab-wizard.py"
