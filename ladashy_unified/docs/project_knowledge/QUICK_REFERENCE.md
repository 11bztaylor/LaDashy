# LaDashy Quick Reference Card

## 🚀 Essential Commands

### Start Everything
```bash
# Terminal 1 - API
cd /home/zach/homelab-documentation/ladashy_unified
source ../homelab-env/bin/activate
python backend/api.py

# Terminal 2 - Frontend  
cd /home/zach/homelab-documentation/ladashy_unified/frontend
python3 -m http.server 8080

# Browser
http://localhost:8080
```

### Quick Restart
```bash
# Kill and restart API
pkill -f "python backend/api.py"
python backend/api.py
```

---

## 🔍 Find Code Fast

### Python Functions
```bash
# Find function definition
grep -n "def function_name" **/*.py

# Get function with context
grep -A 20 "def test_service" backend/api.py

# Find where used
grep -r "function_name(" .
```

### JavaScript Functions  
```bash
# Find in HTML
grep -n "function functionName" frontend/index.html

# Extract whole function
sed -n '/function discoverServices/,/^}/p' frontend/index.html
```

### API Routes
```bash
# List all routes
grep "@app.route" backend/api.py
```

---

## 🧪 Test Commands

### Test API Endpoints
```bash
# Test discovery
curl http://localhost:5000/api/discover

# Test service connection (Plex example)
curl -X POST http://localhost:5000/api/services/plex/192.168.1.100/test \
  -H "Content-Type: application/json" \
  -d '{"host":"192.168.1.100","port":"32400","token":"YOUR_TOKEN"}'

# Save configuration
curl -X POST http://localhost:5000/api/services/plex/192.168.1.100/config \
  -H "Content-Type: application/json" \
  -d '{"host":"192.168.1.100","port":"32400","token":"YOUR_TOKEN"}'
```

---

## 🐛 Common Fixes

### Problem: Button doesn't work
```javascript
// Check browser console (F12)
// Look for: Uncaught ReferenceError

// Fix: Make sure function exists
function buttonFunction() {
    console.log("Button clicked!");
    // Your code here
}
```

### Problem: API returns 404
```python
# Check route exists
@app.route('/api/your/route', methods=['POST'])

# Check method matches
methods=['GET', 'POST']  # If needed
```

### Problem: CORS errors
```python
# In api.py, verify CORS is enabled
from flask_cors import CORS
CORS(app)
```

### Problem: Import errors
```python
# Check Python path
import sys
sys.path.append('..')

# Or use relative imports
from ..collectors.manager import CollectorManager
```

---

## 📁 Key File Locations

### Backend
- API Routes: `backend/api.py`
- Collectors: `homelab_wizard/collectors/*.py`
- Manager: `homelab_wizard/collectors/manager.py`

### Frontend
- Main UI: `frontend/index.html`
- Icons: `frontend/service-icons.js`

### Services
- Definitions: `homelab_wizard/services/definitions.py`
- Scanner: `homelab_wizard/core/scanner.py`

---

## 🔧 Quick Edits

### Add New Service
```python
# In homelab_wizard/services/definitions.py
"Your Category": [
    {
        "name": "ServiceName",
        "icon": "default",
        "containers": ["container-name"],
        "ports": [8080],
        "description": "Service description"
    }
]
```

### Add Console Log
```javascript
// In any JS function
console.log("Debug:", variableName);
```

### Add Python Debug
```python
# In any Python function
print(f"DEBUG: {variable_name}")
import pprint
pprint.pprint(complex_object)
```

---

## 💾 Git Commands

### Save Work
```bash
git add -A
git commit -m "[SECTION_01] Description of change"
git push
```

### Check Status
```bash
git status
git diff
git log --oneline -10
```

### Undo Changes
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all changes
git reset --hard HEAD
```

---

## 🆘 Error Investigation

### Check API Logs
Look in Terminal 1 for Flask output

### Check Browser Console  
F12 → Console tab → Look for red errors

### Check Network Tab
F12 → Network → Click failed request → Check response

### Add Debug Output
```python
# Temporary debug in Python
import json
print("DEBUG:", json.dumps(data, indent=2))

# In JavaScript
console.log("DEBUG:", JSON.stringify(data, null, 2));
```

---

## 📍 Status Check Commands

### See All Section Status
```bash
grep "Current Status" docs/project_knowledge/PROJECT_MANAGER.md
```

### Check Recent Changes
```bash
git log --oneline -5
git diff --name-only
```

### Find TODOs
```bash
grep -r "TODO\|FIXME\|XXX" --include="*.py" --include="*.js" .
```

---

**Keep this handy during every session! 📌**