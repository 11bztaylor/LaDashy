#!/bin/bash

echo "=== Homelab Documentation Cleanup Script ==="
echo "⚠️  This script will remove files. Review each item!"
echo ""

# Safety check
ACTIVE_PROJECT="ladashy_unified"
ACTIVE_ENV="homelab-env"

if [ ! -d "$ACTIVE_PROJECT" ]; then
    echo "ERROR: Active project $ACTIVE_PROJECT not found!"
    exit 1
fi

echo "Active project: $ACTIVE_PROJECT ✓"
echo "Active environment: $ACTIVE_ENV ✓"
echo ""

# Function to ask for confirmation
confirm() {
    read -p "$1 [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Clean Python cache everywhere except active env
echo "## Cleaning Python cache..."
find . -type d -name "__pycache__" -not -path "./$ACTIVE_ENV/*" -exec rm -rf {} + 2>/dev/null
echo "✓ Python cache cleaned"

# Remove backup files
if confirm "Remove all backup files (.backup, .old, .save)?"; then
    find . -name "*.backup" -o -name "*.old" -o -name "*.save" -not -path "./$ACTIVE_PROJECT/*" -exec rm -f {} +
    echo "✓ Backup files removed"
fi

# List other directories for manual review
echo -e "\n## Directories to review manually:"
for dir in */; do
    if [ "$dir" != "$ACTIVE_PROJECT/" ] && [ "$dir" != "$ACTIVE_ENV/" ] && [ "$dir" != "docs/" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "  - $dir (Size: $size)"
    fi
done

echo -e "\n## Space recovered:"
echo "Before: $(du -sh . 2>/dev/null | cut -f1)"

