# LaDashy Project Code Guide

## Table of Contents
1. [Project Structure Overview](#project-structure-overview)
2. [Critical Code Files](#critical-code-files)
3. [What to Include for Each Problem](#what-to-include-for-each-problem)
4. [Quick Code Extraction Commands](#quick-code-extraction-commands)
5. [Session-Specific File Lists](#session-specific-file-lists)

---

## Project Structure Overview

```
ladashy_unified/
├── backend/
│   └── api.py                    # Flask API server (all endpoints)
├── frontend/
│   ├── index.html               # Main web interface (all UI/JS)
│   ├── service-icons.js         # Icon mappings
│   └── update-icons.js          # Icon utilities
├── homelab_wizard/
│   ├── collectors/              # Service data collectors
│   │   ├── manager.py          # Manages all collectors
│   │   ├── base_collector.py   # Base class
│   │   └── *_collector.py      # Service-specific collectors
│   ├── core/                    # Core functionality
│   │   ├── scanner.py          # Network scanner
│   │   ├── service_detector.py # Service identification
│   │   └── connection_tester.py# Connection testing
│   ├── generators/              # Documentation generators
│   │   └── documentation_generator.py
│   └── services/                # Service definitions
│       ├── definitions.py      # All supported services
│       └── icons.py            # Icon data
└── docs/
    └── project_knowledge/       # Living documentation
```

---

## Critical Code Files

### 1. Backend API (`ladashy_unified/backend/`)
- **`api.py`** - Main Flask API server
  - `/api/discover` - Network discovery endpoint
  - `/api/services/{name}/{host}/test` - Test connection (BROKEN)
  - `/api/services/{name}/{host}/config` - Save configuration
  - `/api/dashboard/generate` - Generate Dashy YAML

### 2. Frontend (`ladashy_unified/frontend/`)
- **`index.html`** - Complete web interface containing:
  - All HTML structure
  - All JavaScript functions
  - Button onclick handlers
  - Service grid management
  - API communication

### 3. Service Collectors (`homelab_wizard/collectors/`)
- **`manager.py`** - CollectorManager class (get_collector method)
- **`base_collector.py`** - BaseCollector all services inherit
- **`plex_collector.py`**, **`radarr_collector.py`**, etc. - Service-specific

### 4. Core Modules (`homelab_wizard/core/`)
- **`scanner.py`** - NetworkScanner class
- **`service_detector.py`** - Service identification logic
- **`connection_tester.py`** - Tests service connections

### 5. Service Definitions (`homelab_wizard/services/`)
- **`definitions.py`** - SERVICES dictionary with all supported services
- **`icons.py`** - Icon mappings and data

---

## What to Include for Each Problem

### SECTION_01: Backend API Issues
**Always include:**
1. From `backend/api.py`:
   - The specific route (e.g., `@app.route('/api/services/<name>/<host>/test')`)
   - The function handling it
2. If collector-related:
   - `homelab_wizard/collectors/manager.py` (get_collector method)
   - Specific collector (e.g., `plex_collector.py`)

### SECTION_02: Frontend/Button Issues
**Always include:**
1. From `frontend/index.html`:
   - The button HTML: `<button onclick="functionName()">`
   - The JavaScript function: `function functionName() { ... }`
   - Any functions it calls
2. Browser console errors (F12 → Console)

### SECTION_03: Icon System Issues
**Always include:**
1. `frontend/service-icons.js` (entire file)
2. From `frontend/index.html`:
   - Icon loading code
   - Image tag generation
3. `homelab_wizard/services/icons.py`

### SECTION_04: Dashboard Generation
**Always include:**
1. From `backend/api.py`:
   - `/api/dashboard/generate` endpoint
2. `homelab_wizard/generators/documentation_generator.py`
3. Example of expected output format

### SECTION_05: Service Detection/Collectors
**Always include:**
1. `homelab_wizard/core/service_detector.py`
2. `homelab_wizard/services/definitions.py` (service being added)
3. New collector file being created

---

## Quick Code Extraction Commands

### Extract Python Functions
```bash
# Get specific function with context
grep -A 20 "def test_service" backend/api.py

# Get class and its methods
sed -n '/class CollectorManager/,/^class/p' homelab_wizard/collectors/manager.py

# Find all routes in API
grep "@app.route" backend/api.py
```

### Extract JavaScript Functions
```bash
# Get specific JavaScript function
sed -n '/function discoverServices/,/^[[:space:]]*}/p' frontend/index.html

# Find all onclick handlers
grep -n "onclick" frontend/index.html

# Get function and nested functions
awk '/function addManualService/,/^}/' frontend/index.html
```

### Find Usage Across Project
```bash
# Find where something is imported/used
grep -r "get_collector" homelab_wizard/

# Find all imports of a module
grep -r "from.*manager import" .

# Find JavaScript function calls
grep -r "discoverServices()" frontend/
```

### Quick Status Checks
```bash
# See all API endpoints
grep "@app.route" backend/api.py | sed 's/.*route(//' | sed 's/).*//'

# List all collectors
ls homelab_wizard/collectors/*_collector.py

# Check for TODO/FIXME
grep -r "TODO\|FIXME" --include="*.py" --include="*.js" .
```

---

## Session-Specific File Lists

### Quick Copy Commands for Each Section

#### SECTION_01 (Backend API Fix)
```bash
# Extract broken test endpoint
sed -n '/@app.route.*test/,/^@app.route\|^def [^t]\|^class/p' backend/api.py > section01_code.txt
grep -A 15 "def get_collector" homelab_wizard/collectors/manager.py >> section01_code.txt
```

#### SECTION_02 (Frontend Buttons)
```bash
# Extract button functions
grep -B2 -A2 "onclick" frontend/index.html > section02_code.txt
echo "=== DISCOVER FUNCTION ===" >> section02_code.txt
sed -n '/function discoverServices/,/^}/p' frontend/index.html >> section02_code.txt
```

#### SECTION_03 (Icons)
```bash
# Get icon-related code
cat frontend/service-icons.js > section03_code.txt
echo "=== ICON LOADING FROM HTML ===" >> section03_code.txt
grep -A5 -B5 "icon" frontend/index.html >> section03_code.txt
```

---

## Most Common File Combinations

### 90% of issues need these files:

1. **Backend Issues**
   - `backend/api.py`
   - `homelab_wizard/collectors/manager.py`

2. **Frontend Issues**
   - `frontend/index.html` (specific functions)
   - Browser console output

3. **Service Connection Issues**
   - `backend/api.py` (test endpoint)
   - `homelab_wizard/collectors/manager.py`
   - Specific collector file

4. **Service Detection Issues**
   - `homelab_wizard/core/service_detector.py`
   - `homelab_wizard/services/definitions.py`

---

## Quick Session Prep Template

```bash
# Before starting any session, run:
SECTION=01  # Change to your section number

# Create context file
echo "Working on SECTION_${SECTION}" > session_context.txt
echo "Files needed:" >> session_context.txt

# Add file list based on section
case $SECTION in
  01) echo "- backend/api.py (test_service function)" >> session_context.txt
      echo "- homelab_wizard/collectors/manager.py" >> session_context.txt ;;
  02) echo "- frontend/index.html (button functions)" >> session_context.txt ;;
  03) echo "- frontend/service-icons.js" >> session_context.txt ;;
esac

cat session_context.txt
```

---

## Running LaDashy

### Start Commands
```bash
cd /home/zach/homelab-documentation/ladashy_unified
source ../homelab-env/bin/activate

# Terminal 1: API Backend
python backend/api.py

# Terminal 2: Frontend Server
cd frontend && python3 -m http.server 8080

# Browser: http://localhost:8080
```

### Test Commands
```bash
# Test API endpoint
curl http://localhost:5000/api/discover

# Test service connection
curl -X POST http://localhost:5000/api/services/plex/192.168.1.100/test \
  -H "Content-Type: application/json" \
  -d '{"host":"192.168.1.100","port":"32400","token":"xxx"}'
```

---

## Notes
- Always include actual code, not just descriptions
- Include error messages from browser console
- Test fixes incrementally
- Update docs/project_knowledge/ after each fix