#!/bin/bash

echo "=== SAFE Cleanup - Only Removing Confirmed Unused Files ==="
echo ""

ACTIVE_PROJECT="ladashy_unified"
ACTIVE_ENV="homelab-env"

# Things that are DEFINITELY safe to remove
echo "## Removing definitely safe items..."

# Python cache outside our project
find . -type d -name "__pycache__" -not -path "./$ACTIVE_PROJECT/*" -not -path "./$ACTIVE_ENV/*" -exec rm -rf {} + 2>/dev/null
echo "✓ Removed Python cache outside project"

# Old log files
find . -name "*.log" -not -path "./$ACTIVE_PROJECT/*" -mtime +7 -exec rm -f {} + 2>/dev/null
echo "✓ Removed old log files"

# Backup files outside project
find . \( -name "*.backup" -o -name "*.bak" -o -name "*~" \) -not -path "./$ACTIVE_PROJECT/*" -exec rm -f {} + 2>/dev/null
echo "✓ Removed backup files"

echo -e "\n## Directories that need manual review:"
echo "Run: ls -la"
echo "Then for each directory that isn't 'ladashy_unified' or 'homelab-env':"
echo "  1. Check if it's an old version: ls <directory>/"
echo "  2. If it looks like old LaDashy code: rm -rf <directory>/"

echo -e "\n## DO NOT REMOVE:"
echo "- ladashy_unified/ (active project)"
echo "- homelab-env/ (Python environment)"
echo "- Any directory you're not sure about"

