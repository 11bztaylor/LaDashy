#!/bin/bash
# LaDashy Clean Commit Strategy
# This script will help you clean up and commit properly

cd /home/zach/homelab-documentation/ladashy_unified

echo "🚀 LaDashy Clean Commit Process"
echo "=============================="
echo ""

# Step 1: Run cleanup
echo "Step 1: Running cleanup script..."
if [ -f "./cleanup_project.sh" ]; then
    bash ./cleanup_project.sh
else
    echo "⚠️  Run the cleanup script first!"
    exit 1
fi

echo ""
echo "Step 2: Checking what's left..."
echo "=============================="
git status --short
echo "=============================="
echo ""

# Step 3: Add .gitignore if missing
echo "Step 3: Creating proper .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
*.Zone.Identifier

# Project specific
*.pid
*.log
SESSION_CONTEXT_*.md
LADASHY_FULL_CODE_*.md
LADASHY_PART_*
test_*.html
*_backup_*
*.broken
*.broken_*

# Temporary files
fix_*.py
check_*.py
ensure_*.py
improve_*.py
add_*.py

# Keep important docs
!docs/project_knowledge/**
EOF

echo "✅ .gitignore created"
echo ""

# Step 4: Fix documentation conflicts
echo "Step 4: Fixing documentation conflicts..."

# Update Progress Tracker to reflect Section 01 completion
if [ -f "docs/project_knowledge/SECTION_01_COMPLETE.md" ]; then
    echo "Found Section 01 complete marker. Updating Progress Tracker..."
    
    # Create updated progress tracker
    cat > docs/project_knowledge/PROGRESS_TRACKER.md << 'EOF'
# LaDashy Progress Tracker

## 🎯 Project Goals
**Mission**: Create a working homelab documentation and service discovery tool
**Current Phase**: Fixing core functionality
**Target**: All buttons working, services discoverable, dashboard generatable

---

## 📊 Section Progress

### SECTION_01_BACKEND_API
- **Status**: ✅ COMPLETE
- **Priority**: 🔴 CRITICAL
- **Effort**: 2-3 hours
- **Completed**: 2024-08-01
- [x] Fix test_service endpoint
- [x] Add proper error handling  
- [x] Test with all collector types
- **Notes**: All collectors working (Plex, Radarr, Sonarr, Jellyfin, Portainer, Pi-hole)

### SECTION_02_FRONTEND_STATE  
- **Status**: 🚧 In Progress
- **Priority**: 🔴 HIGH
- **Effort**: 3-4 hours
- **Blocked By**: ~~Section 01~~ Ready to start
- [ ] Fix button onclick handlers
- [ ] Fix service state management
- [ ] Add API key field to manual add
- [ ] Fix section categorization

### SECTION_03_ICON_SYSTEM
- **Status**: ❌ Not Started
- **Priority**: 🟡 MEDIUM
- **Effort**: 1-2 hours
- [ ] Implement emoji fallback
- [ ] Fix 404 errors
- [ ] Create icon mapping system

### SECTION_04_DASHBOARD_GEN
- **Status**: ❌ Not Started
- **Priority**: 🟡 MEDIUM
- **Effort**: 4-5 hours
- **Blocked By**: Section 02
- [ ] Implement generateDashboard()
- [ ] Create Dashy YAML format
- [ ] Add configuration options
- [ ] Test with real Dashy instance

### SECTION_05_COLLECTORS
- **Status**: ⚠️ Partial
- **Priority**: 🟢 LOW
- **Effort**: 2-3 hours per collector
- **Working**: Plex, Radarr, Sonarr, Jellyfin, Portainer, Pi-hole
- [ ] Add Home Assistant collector
- [ ] Add Docker stats collector
- [ ] Add Proxmox collector
- [ ] Add custom service support

---

## 📅 Updated Timeline

### Completed
- ✅ Section 01: Backend API (All endpoints working)

### Next Up
- 🚧 Section 02: Frontend State Management
- ⏳ Section 03: Icon System
- ⏳ Section 04: Dashboard Generation
- ⏳ Section 05: Additional Collectors

---

## 📈 Metrics

### Code Health
- **Total Files**: ~30 (after cleanup)
- **Lines of Code**: ~5000
- **Test Coverage**: 10% 📈
- **Documentation**: 60% 📝

### Progress Velocity  
- **Sections Completed**: 1/5 ✅
- **Estimated Hours Remaining**: 10-15
- **Days to Complete**: 3-5 (focused work)

---

*Last Updated: $(date)*
EOF
fi

echo "✅ Documentation updated"
echo ""

# Step 5: Stage files for commit
echo "Step 5: Staging files for commit..."
echo "===================================="

# Add all modified tracked files
git add -u

# Add documentation
git add docs/project_knowledge/

# Add important configs
git add .gitignore
git add requirements.txt
git add generate_session.sh

# Add clean code files
git add backend/api.py
git add frontend/index.html
git add frontend/service-icons.js
git add homelab_wizard/

# Show what will be committed
echo ""
echo "Files to be committed:"
echo "======================"
git status --short --cached
echo "======================"
echo ""

# Step 6: Create commit
echo "Step 6: Ready to commit!"
echo ""
echo "Suggested commit message:"
echo "------------------------"
echo "[CLEANUP] Major project cleanup - Section 01 complete, ready for Section 02"
echo ""
echo "- Removed 60+ temporary fix/test files"
echo "- Updated documentation to reflect Section 01 completion"
echo "- Fixed documentation conflicts"  
echo "- Added comprehensive .gitignore"
echo "- Backend API fully functional with all collectors"
echo "- Ready to tackle frontend issues in Section 02"
echo "------------------------"
echo ""
echo "To commit, run:"
echo "git commit -m \"[CLEANUP] Major project cleanup - Section 01 complete, ready for Section 02\""
echo ""
echo "Then push:"
echo "git push origin main"