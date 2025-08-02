#!/bin/bash
# LaDashy Project Cleanup Script
# This will remove all temporary files while preserving important work

cd /home/zach/homelab-documentation/ladashy_unified

echo "🧹 Starting LaDashy cleanup..."

# Create backup just in case
echo "📦 Creating safety backup..."
tar -czf ../ladashy_backup_$(date +%Y%m%d_%H%M%S).tar.gz . 2>/dev/null

# Remove all temporary fix scripts
echo "🗑️  Removing temporary fix scripts..."
rm -f fix_*.py
rm -f check_*.py
rm -f ensure_*.py
rm -f add_*.py
rm -f save_*.py
rm -f thorough_*.py

# Remove test files
echo "🗑️  Removing test files..."
rm -f test_*.html
rm -f current_index.html
rm -f javascript_section.txt

# Remove broken backups
echo "🗑️  Removing broken file backups..."
rm -f frontend/index.html.broken*
rm -f frontend/index.html.test
rm -f frontend/.index.html.swp

# Remove Zone.Identifier files (Windows artifacts)
echo "🗑️  Removing Windows Zone.Identifier files..."
find . -name "*.Zone.Identifier" -delete

# Remove temporary session files (keep the latest one)
echo "🗑️  Cleaning up old session files..."
ls -t SESSION_CONTEXT_*.md | tail -n +2 | xargs rm -f

# Remove split files
echo "🗑️  Removing split documentation files..."
rm -f LADASHY_PART_*
rm -f LADASHY_FULL_CODE_*.md

# Remove PID and log files
echo "🗑️  Removing PID and log files..."
rm -f *.pid
rm -f frontend/*.pid
rm -f *.log
rm -f frontend/*.log

# Remove misc temp files
echo "🗑️  Removing miscellaneous temp files..."
rm -f create_safe_file.sh
rm -f backend_status*.txt
rm -f dashboard_with_radarr.yaml
rm -f generated_dashboard.yaml

# Remove Python cache
echo "🗑️  Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Clean up frontend subdirectory
echo "🗑️  Cleaning frontend directory..."
rm -f frontend/fix_*.py
rm -f frontend/add_*.py
rm -f frontend/improve_*.py
rm -f frontend/SESSION_*.md
rm -f frontend/restart_ladashy.sh
rm -f frontend/frontend.log

# Show what's left
echo ""
echo "✅ Cleanup complete! Here's what remains:"
echo "===================================="
git status --short
echo "===================================="
echo ""
echo "📊 File count before: $(git status --short | wc -l)"
echo "📊 File count after: Should be much less!"
echo ""
echo "💡 Next steps:"
echo "1. Review remaining files with: git status"
echo "2. Add the files you want to keep"
echo "3. Commit your clean project"
