#!/bin/bash

echo "=== Finding ALL Files Used by LaDashy ==="
echo ""

ACTIVE_PROJECT="ladashy_unified"
cd "$ACTIVE_PROJECT"

# Create a list of files that are definitely used
echo "## Creating list of files LaDashy needs..."

# Start with entry points
{
    echo "backend/api.py"
    echo "frontend/index.html"
    echo "frontend/service-icons.js"
    echo "frontend/update-icons.js"
} > used_files.txt

# Find all Python imports from the entry point
echo "## Tracing Python dependencies from backend/api.py..."
python3 << 'PYEOF'
import os
import ast
import sys

used_files = set()
checked_files = set()

def find_imports(filepath):
    if filepath in checked_files:
        return
    checked_files.add(filepath)
    
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    used_files.add(f"Import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if module.startswith('homelab_wizard') or module.startswith('.'):
                    # Local import
                    parts = module.split('.')
                    if parts[0] == 'homelab_wizard':
                        path = os.path.join(*parts) + '.py'
                        if os.path.exists(path):
                            used_files.add(path)
                            find_imports(path)
                    for alias in node.names:
                        used_files.add(f"From {module} import {alias.name}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

# Start from api.py
find_imports('backend/api.py')

# Check all homelab_wizard modules
for root, dirs, files in os.walk('homelab_wizard'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            used_files.add(filepath)

# Print all used files
for f in sorted(used_files):
    print(f)
PYEOF

# Find all JavaScript dependencies
echo -e "\n## JavaScript files referenced in HTML..."
grep -h "\.js\|\.css" frontend/index.html | grep -oE '["\x27][^"\x27]*\.(js|css)["\x27]' | tr -d '"' | tr -d "'" | sort -u

# Find all service definitions
echo -e "\n## Finding all collector modules..."
find homelab_wizard/collectors -name "*.py" -type f

# Find configuration files
echo -e "\n## Configuration and data files..."
find . -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.ini" -o -name "*.conf" 2>/dev/null

# Find all asset files
echo -e "\n## Asset files (icons, images)..."
find . -name "*.png" -o -name "*.jpg" -o -name "*.svg" -o -name "*.ico" 2>/dev/null

# Now check what's in the parent directory that might be needed
cd ..
echo -e "\n## Checking parent directory for dependencies..."

# The virtual environment we need
echo "- homelab-env/ (Virtual environment - REQUIRED)"

# Check if any other directories are referenced
grep -r "$ACTIVE_PROJECT\|homelab_wizard" . --include="*.py" --include="*.sh" --exclude-dir="$ACTIVE_PROJECT" --exclude-dir=".git" 2>/dev/null

echo -e "\n## Summary of what LaDashy NEEDS:"
echo "1. Everything in ladashy_unified/"
echo "2. The homelab-env/ virtual environment"
echo "3. Any shared libraries installed in homelab-env"

echo -e "\n## Safe to remove:"
for dir in */; do
    if [ "$dir" != "$ACTIVE_PROJECT/" ] && [ "$dir" != "homelab-env/" ]; then
        # Check if it's referenced anywhere
        if ! grep -r "$dir" "$ACTIVE_PROJECT" >/dev/null 2>&1; then
            echo "- $dir (not referenced by LaDashy)"
        fi
    fi
done

