#!/bin/bash

echo "=== Identifying Potentially Unused Items ==="
echo ""

ACTIVE_PROJECT="ladashy_unified"
ACTIVE_ENV="homelab-env"

echo "## Active Components:"
echo "- Project: $ACTIVE_PROJECT"
echo "- Virtual Env: $ACTIVE_ENV"
echo ""

echo "## Potentially Unused (Safe to Remove):"

# Old virtual environments
echo -e "\n### Old Virtual Environments:"
for dir in */; do
    if [ -f "$dir/bin/activate" ] && [ "$dir" != "$ACTIVE_ENV/" ]; then
        echo "  - $dir (Virtual environment - not the active one)"
    fi
done

# Old project versions
echo -e "\n### Possible Old Project Versions:"
for dir in */; do
    dir_name=$(basename "$dir")
    # Skip our active project and env
    if [ "$dir_name" != "$ACTIVE_PROJECT" ] && [ "$dir_name" != "$ACTIVE_ENV" ]; then
        # Check if it looks like a project
        if [ -f "$dir/setup.py" ] || [ -f "$dir/main.py" ] || [ -f "$dir/app.py" ] || [ -d "$dir/.git" ]; then
            size=$(du -sh "$dir" 2>/dev/null | cut -f1)
            echo "  - $dir (Size: $size)"
            
            # Check if it has similar files to our active project
            if [ -f "$dir/backend/api.py" ] || [ -d "$dir/homelab_wizard" ]; then
                echo "    ⚠️  LIKELY OLD VERSION OF LADASHY"
            fi
        fi
    fi
done

# Backup files
echo -e "\n### Backup Files:"
find . -name "*.backup" -o -name "*.old" -o -name "*.save" -o -name "*_backup*" | grep -v "$ACTIVE_PROJECT"

# Log files
echo -e "\n### Log Files:"
find . -name "*.log" -o -name "*.out" | grep -v "$ACTIVE_PROJECT"

# Create removal commands (but don't execute)
echo -e "\n## Suggested Removal Commands (REVIEW FIRST):"
echo "# To remove old virtual environments:"
for dir in */; do
    if [ -f "$dir/bin/activate" ] && [ "$dir" != "$ACTIVE_ENV/" ]; then
        echo "rm -rf $dir"
    fi
done

