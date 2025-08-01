#!/bin/bash

echo "=== Homelab Documentation Directory Analysis ==="
echo "Generated: $(date)"
echo ""

# First, show the top-level structure
echo "## Top-Level Directory Structure:"
ls -la --color=never | grep -v "^total"

echo -e "\n## Directory Sizes:"
du -sh */ 2>/dev/null | sort -hr

echo -e "\n## Python Virtual Environments Found:"
find . -maxdepth 2 -name "bin" -type d | while read bindir; do
    if [ -f "$bindir/activate" ]; then
        echo "  - $(dirname "$bindir")"
    fi
done

echo -e "\n## Git Repositories Found:"
find . -maxdepth 2 -name ".git" -type d | while read gitdir; do
    repo_path=$(dirname "$gitdir")
    echo "  - $repo_path"
    # Check if it's the active LaDashy project
    if [ "$repo_path" == "./ladashy_unified" ]; then
        echo "    ^ ACTIVE PROJECT"
    else
        # Check last commit date
        last_commit=$(cd "$repo_path" && git log -1 --format="%cr" 2>/dev/null || echo "unknown")
        echo "    Last commit: $last_commit"
    fi
done

echo -e "\n## Potential Duplicate Projects:"
# Look for similar named directories
find . -maxdepth 2 -type d -name "*ladashy*" -o -name "*homelab*" -o -name "*wizard*" | sort

echo -e "\n## Large Files (>10MB):"
find . -type f -size +10M 2>/dev/null | grep -v ".git" | head -20

echo -e "\n## Recently Modified (last 7 days):"
find . -type f -mtime -7 | grep -v ".git" | grep -v "__pycache__" | sort

echo -e "\n## Checking Project Dependencies:"
# See which directories might be related to ladashy_unified
active_project="ladashy_unified"
echo "Looking for references to $active_project..."

# Check for symlinks
find . -type l -ls 2>/dev/null | grep "$active_project"

# Check for imports or references in Python files
grep -r "ladashy_unified\|homelab_wizard" . --include="*.py" --exclude-dir=".git" --exclude-dir="$active_project" 2>/dev/null | head -10

