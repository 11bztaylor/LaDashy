#!/bin/bash
# Setup and launch the complete web-based LaDashy

echo "=== Setting up Web-based LaDashy with all features ==="

# Ensure we're in the right directory
cd /home/zach/homelab-documentation

# Create the unified structure if it doesn't exist
if [ ! -d "ladashy_unified" ]; then
    mkdir -p ladashy_unified/{backend,frontend,shared}
fi

# Copy all existing homelab_wizard code to shared
echo "📦 Migrating existing code..."
cp -r homelab_wizard ladashy_unified/shared/ 2>/dev/null || echo "Code already migrated"

# Create the enhanced REST API with all features
cat > ladashy_unified/backend/api.py << 'EOFAPI'
"""
LaDashy REST API - Complete Implementation
Backend service with all features from the desktop version
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import sys
import os
import json
import threading
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared'))

# Import all our modules
from homelab_wizard.core.scanner import NetworkScanner
from homelab_wizard.generators.documentation_generator import DocumentationGenerator
from homelab_wizard.collectors.manager import CollectorManager
from homelab_wizard.services.definitions import get_all_services

app = Flask(__name__)
CORS(app)

# Global storage
app.discovered_services = {}
app.service_configs = {}
app.collected_data = {}
app.scan_status = {"scanning": False, "progress": "", "error": None}

# Load saved configs if they exist
config_file = os.path.expanduser("~/.ladashy/service_configs.json")
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        app.service_configs = json.load(f)

@app.route('/')
def index():
    """Redirect to frontend"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "version": "2.0.0",
        "features": ["scan", "collect", "generate", "export"]
    })

@app.route('/api/scan', methods=['POST'])
def scan_network():
    """Start network scan"""
    if app.scan_status["scanning"]:
        return jsonify({"error": "Scan already in progress"}), 400
    
    data = request.json
    networks = data.get('networks', ['192.168.1.0/24'])
    
    def scan_worker():
        app.scan_status["scanning"] = True
        app.scan_status["error"] = None
        scanner = NetworkScanner()
        
        try:
            # Add networks
            for network in networks:
                scanner.add_network(network)
            
            # Progress callback
            def progress_callback(msg):
                app.scan_status["progress"] = msg
            
            # Scan
            app.discovered_services = scanner.discover_all_services(progress_callback)
            app.scan_status["progress"] = "Scan complete!"
            
        except Exception as e:
            app.scan_status["error"] = str(e)
        finally:
            app.scan_status["scanning"] = False
    
    thread = threading.Thread(target=scan_worker, daemon=True)
    thread.start()
    
    return jsonify({"status": "Scan started", "networks": networks})

@app.route('/api/scan/status')
def get_scan_status():
    """Get scan status"""
    total_services = sum(len(h.get('services', [])) for h in app.discovered_services.values())
    
    return jsonify({
        "scanning": app.scan_status["scanning"],
        "progress": app.scan_status["progress"],
        "error": app.scan_status["error"],
        "hosts_found": len(app.discovered_services),
        "services_found": total_services
    })

@app.route('/api/services')
def get_services():
    """Get discovered services"""
    return jsonify(app.discovered_services)

@app.route('/api/services/<service_name>/<host>/config', methods=['GET', 'POST'])
def service_config(service_name, host):
    """Get or update service configuration"""
    service_key = f"{service_name}_{host}"
    
    if request.method == 'GET':
        return jsonify(app.service_configs.get(service_key, {}))
    else:
        config = request.json
        app.service_configs[service_key] = config
        
        # Save to file
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(app.service_configs, f, indent=2)
        
        # Try to collect data
        manager = CollectorManager()
        service_info = next(
            (s for h in app.discovered_services.values() 
             for s in h.get('services', []) 
             if s['name'] == service_name and h.get('ip') == host),
            None
        )
        
        if service_info:
            collector = manager.get_collector(service_name.lower())
            if collector:
                port = service_info['ports'][0] if service_info.get('ports') else 8080
                
                if collector.test_connection(host, port, config):
                    basic = collector.collect_basic_info(host, port, config)
                    detailed = collector.collect_detailed_info(host, port, config)
                    
                    app.collected_data[service_key] = {
                        **basic,
                        **detailed,
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    return jsonify({
                        "status": "Configuration saved and data collected",
                        "data": app.collected_data[service_key]
                    })
        
        return jsonify({"status": "Configuration saved"})

@app.route('/api/services/<service_name>/<host>/test', methods=['POST'])
def test_service(service_name, host):
    """Test service connection"""
    config = request.json
    manager = CollectorManager()
    collector = manager.get_collector(service_name.lower())
    
    if not collector:
        return jsonify({"error": "No collector available for this service"}), 404
    
    # Find service port
    port = 8080
    for h_ip, h_info in app.discovered_services.items():
        if h_ip == host:
            for svc in h_info.get('services', []):
                if svc['name'] == service_name:
                    port = svc['ports'][0] if svc.get('ports') else 8080
                    break
    
    if collector.test_connection(host, port, config):
        return jsonify({"status": "success", "message": "Connection successful!"})
    else:
        return jsonify({"status": "failed", "message": "Could not connect to service"}), 400

@app.route('/api/services/definitions')
def get_service_definitions():
    """Get all service definitions"""
    return jsonify(get_all_services())

@app.route('/api/generate', methods=['POST'])
def generate_documentation():
    """Generate documentation"""
    data = request.json
    options = data.get('options', {})
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Generate documentation
            generator = DocumentationGenerator(temp_dir)
            results = generator.generate_all(
                app.discovered_services,
                app.service_configs,
                app.collected_data
            )
            
            # Export additional formats
            if options.get('json', True):
                generator.export_to_json(
                    app.discovered_services,
                    app.service_configs,
                    app.collected_data
                )
            
            if options.get('html', True):
                generator.export_to_html_dashboard(
                    app.discovered_services,
                    app.service_configs
                )
            
            # Create zip file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"ladashy_docs_{timestamp}.zip"
            zip_path = Path(temp_dir) / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != zip_filename:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=zip_filename,
                mimetype='application/zip'
            )
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/state/save', methods=['POST'])
def save_state():
    """Save current state"""
    state = {
        'discovered_services': app.discovered_services,
        'service_configs': app.service_configs,
        'collected_data': app.collected_data,
        'timestamp': datetime.now().isoformat()
    }
    
    state_file = os.path.expanduser("~/.ladashy/state_backup.json")
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    return jsonify({"status": "State saved", "file": state_file})

@app.route('/api/state/load', methods=['POST'])
def load_state():
    """Load saved state"""
    state_file = os.path.expanduser("~/.ladashy/state_backup.json")
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        app.discovered_services = state.get('discovered_services', {})
        app.service_configs = state.get('service_configs', {})
        app.collected_data = state.get('collected_data', {})
        
        return jsonify({
            "status": "State loaded",
            "timestamp": state.get('timestamp'),
            "services": sum(len(h.get('services', [])) for h in app.discovered_services.values())
        })
    else:
        return jsonify({"error": "No saved state found"}), 404

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 LaDashy API Server Starting...")
    print("="*50)
    print(f"📡 API URL: http://localhost:5000/api/")
    print(f"🌐 Web UI: http://localhost:8080/")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
EOFAPI

# Create the enhanced frontend with all features
cat > ladashy_unified/frontend/index.html << 'EOFHTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LaDashy - Homelab Documentation Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-tertiary: #3d3d3d;
            --text-primary: #e0e0e0;
            --text-secondary: #b0b0b0;
            --accent-primary: #4ecdc4;
            --accent-secondary: #45b7d1;
            --accent-success: #96ceb4;
            --accent-warning: #ffd93d;
            --accent-error: #ff6b6b;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            color: var(--accent-primary);
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header-actions {
            display: flex;
            gap: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--bg-secondary);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card h3 {
            color: var(--accent-success);
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--accent-primary);
        }
        
        .controls {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .btn {
            background: var(--accent-primary);
            color: var(--bg-primary);
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            font-size: 1em;
            margin-right: 10px;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn:hover {
            background: var(--accent-secondary);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(78, 205, 196, 0.3);
        }
        
        .btn:disabled {
            background: #555;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }
        
        .btn-secondary:hover {
            background: #4d4d4d;
        }
        
        .services {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .service-card {
            background: var(--bg-tertiary);
            padding: 20px;
            border-radius: 8px;
            transition: all 0.3s;
            border: 1px solid transparent;
            position: relative;
        }
        
        .service-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
            border-color: var(--accent-primary);
        }
        
        .service-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        
        .service-name {
            color: var(--accent-primary);
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        
        .service-info {
            font-size: 0.9em;
            color: var(--text-secondary);
            line-height: 1.8;
        }
        
        .service-status {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9em;
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .status-configured { background: var(--accent-success); }
        .status-discovered { background: var(--accent-warning); }
        .status-error { background: var(--accent-error); }
        
        .service-actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 0.85em;
        }
        
        .progress {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .progress.active { display: block; }
        
        .progress-text {
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .progress-bar {
            background: var(--bg-tertiary);
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            height: 100%;
            width: 0%;
            transition: width 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .option {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px;
            background: var(--bg-tertiary);
            border-radius: 5px;
            transition: background 0.2s;
        }
        
        .option:hover {
            background: #4d4d4d;
        }
        
        .option input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: var(--accent-primary);
        }
        
        .option label {
            cursor: pointer;
            flex: 1;
        }
        
        .network-input {
            background: var(--bg-tertiary);
            border: 1px solid #555;
            color: var(--text-primary);
            padding: 12px;
            border-radius: 5px;
            width: 100%;
            margin-bottom: 15px;
            font-size: 1em;
        }
        
        .network-input:focus {
            outline: none;
            border-color: var(--accent-primary);
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            overflow-y: auto;
        }
        
        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 10px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h2 {
            color: var(--accent-primary);
        }
        
        .close-btn {
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 1.5em;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 5px;
            transition: background 0.2s;
        }
        
        .close-btn:hover {
            background: var(--bg-tertiary);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 10px;
            background: var(--bg-tertiary);
            border: 1px solid #555;
            color: var(--text-primary);
            border-radius: 5px;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--accent-primary);
        }
        
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--bg-secondary);
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            display: none;
            align-items: center;
            gap: 10px;
            z-index: 2000;
        }
        
        .toast.show {
            display: flex;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .toast.success {
            border-left: 4px solid var(--accent-success);
        }
        
        .toast.error {
            border-left: 4px solid var(--accent-error);
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }
        
        .empty-state h3 {
            color: var(--text-primary);
            margin-bottom: 10px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--bg-tertiary);
        }
        
        .tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }
        
        .tab:hover {
            color: var(--text-primary);
        }
        
        .tab.active {
            color: var(--accent-primary);
            border-bottom-color: var(--accent-primary);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🏠 LaDashy</h1>
                <p>Homelab Documentation Generator</p>
            </div>
            <div class="header-actions">
                <button class="btn btn-secondary" onclick="saveState()">💾 Save State</button>
                <button class="btn btn-secondary" onclick="loadState()">📂 Load State</button>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Hosts Found</h3>
                <div class="value" id="stat-hosts">0</div>
            </div>
            <div class="stat-card">
                <h3>Services</h3>
                <div class="value" id="stat-services">0</div>
            </div>
            <div class="stat-card">
                <h3>Configured</h3>
                <div class="value" id="stat-configured">0</div>
            </div>
            <div class="stat-card">
                <h3>Data Collected</h3>
                <div class="value" id="stat-collected">0</div>
            </div>
        </div>

        <div class="controls">
            <h2>Network Scanner</h2>
            <div style="margin: 20px 0;">
                <label>Network Range (comma-separated for multiple):</label>
                <input type="text" id="network-range" class="network-input" 
                       value="192.168.1.0/24" placeholder="192.168.1.0/24, 10.0.0.0/24">
            </div>
            <button class="btn" id="btn-scan" onclick="startScan()">
                <span>🔍</span> Scan Network
            </button>
            <button class="btn" id="btn-generate" onclick="showGenerateOptions()" disabled>
                <span>📄</span> Generate Documentation
            </button>
            <button class="btn btn-secondary" onclick="showServiceDefinitions()">
                <span>📋</span> Service Definitions
            </button>
        </div>

        <div class="progress" id="progress">
            <div class="progress-text" id="progress-text">Initializing scan...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
        </div>

        <div class="services" id="services" style="display: none;">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('discovered')">Discovered Services</button>
                <button class="tab" onclick="switchTab('configured')">Configured Services</button>
                <button class="tab" onclick="switchTab('collected')">Collected Data</button>
            </div>
            
            <div class="tab-content active" id="tab-discovered">
                <div class="service-grid" id="service-grid"></div>
            </div>
            
            <div class="tab-content" id="tab-configured">
                <div class="service-grid" id="configured-grid"></div>
            </div>
            
            <div class="tab-content" id="tab-collected">
                <div class="service-grid" id="collected-grid"></div>
            </div>
        </div>

        <!-- Service Configuration Modal -->
        <div class="modal" id="config-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="config-title">Configure Service</h2>
                    <button class="close-btn" onclick="closeConfigModal()">×</button>
                </div>
                <div id="config-form"></div>
            </div>
        </div>

        <!-- Generate Options Modal -->
        <div class="modal" id="generate-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Documentation Options</h2>
                    <button class="close-btn" onclick="hideGenerateOptions()">×</button>
                </div>
                <div class="options">
                    <div class="option">
                        <input type="checkbox" id="opt-network" checked>
                        <label for="opt-network">Network Topology Diagram</label>
                    </div>
                    <div class="option">
                        <input type="checkbox" id="opt-dependencies" checked>
                        <label for="opt-dependencies">Service Dependencies</label>
                    </div>
                    <div class="option">
                        <input type="checkbox" id="opt-docker" checked>
                        <label for="opt-docker">Docker Compose Files</label>
                    </div>
                    <div class="option">
                        <input type="checkbox" id="opt-security" checked>
                        <label for="opt-security">Security Audit</label>
                    </div>
                    <div class="option">
                        <input type="checkbox" id="opt-json" checked>
                        <label for="opt-json">JSON Export</label>
                    </div>
                    <div class="option">
                        <input type="checkbox" id="opt-html" checked>
                        <label for="opt-html">HTML Dashboard</label>
                    </div>
                </div>
                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button class="btn" onclick="generateDocs()">
                        <span>🚀</span> Generate & Download
                    </button>
                    <button class="btn btn-secondary" onclick="hideGenerateOptions()">Cancel</button>
                </div>
            </div>
        </div>

        <!-- Toast Notification -->
        <div class="toast" id="toast">
            <span id="toast-message"></span>
        </div>
    </div>

    <script>
        const API_URL = 'http://localhost:5000/api';
        let scanInterval = null;
        let services = {};
        let configs = {};
        let collectedData = {};
        let currentService = null;

        async function startScan() {
            const networks = document.getElementById('network-range').value
                .split(',')
                .map(n => n.trim())
                .filter(n => n);
            
            if (networks.length === 0) {
                showToast('Please enter at least one network range', 'error');
                return;
            }
            
            document.getElementById('btn-scan').disabled = true;
            document.getElementById('progress').classList.add('active');
            document.getElementById('services').style.display = 'none';
            
            try {
                const response = await fetch(`${API_URL}/scan`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ networks })
                });
                
                if (response.ok) {
                    showToast('Network scan started!', 'success');
                    scanInterval = setInterval(checkScanStatus, 1000);
                } else {
                    throw new Error('Failed to start scan');
                }
            } catch (error) {
                showToast('Failed to start scan: ' + error.message, 'error');
                document.getElementById('btn-scan').disabled = false;
                document.getElementById('progress').classList.remove('active');
            }
        }

        async function checkScanStatus() {
            try {
                const response = await fetch(`${API_URL}/scan/status`);
                const status = await response.json();
                
                document.getElementById('progress-text').textContent = status.progress || 'Scanning...';
                document.getElementById('stat-hosts').textContent = status.hosts_found || 0;
                document.getElementById('stat-services').textContent = status.services_found || 0;
                
                // Update progress bar
                if (status.progress.includes('complete')) {
                    document.getElementById('progress-fill').style.width = '100%';
                } else {
                    // Estimate progress
                    const progress = Math.min((status.services_found || 0) * 10, 90);
                    document.getElementById('progress-fill').style.width = progress + '%';
                }
                
                if (!status.scanning) {
                    clearInterval(scanInterval);
                    document.getElementById('btn-scan').disabled = false;
                    document.getElementById('progress').classList.remove('active');
                    
                    if (status.error) {
                        showToast('Scan error: ' + status.error, 'error');
                    } else {
                        showToast('Scan complete!', 'success');
                        loadServices();
                    }
                }
            } catch (error) {
                console.error('Status check error:', error);
            }
        }

        async function loadServices() {
            try {
                const response = await fetch(`${API_URL}/services`);
                services = await response.json();
                
                updateServiceGrid();
                document.getElementById('services').style.display = 'block';
                document.getElementById('btn-generate').disabled = Object.keys(services).length === 0;
                
                // Update stats
                let totalServices = 0;
                let configuredCount = 0;
                
                for (const [ip, hostInfo] of Object.entries(services)) {
                    for (const service of hostInfo.services || []) {
                        totalServices++;
                        const key = `${service.name}_${ip}`;
                        if (configs[key]) configuredCount++;
                    }
                }
                
                document.getElementById('stat-hosts').textContent = Object.keys(services).length;
                document.getElementById('stat-services').textContent = totalServices;
                document.getElementById('stat-configured').textContent = configuredCount;
                document.getElementById('stat-collected').textContent = Object.keys(collectedData).length;
                
            } catch (error) {
                showToast('Failed to load services: ' + error.message, 'error');
            }
        }

        function updateServiceGrid() {
            const grid = document.getElementById('service-grid');
            grid.innerHTML = '';
            
            if (Object.keys(services).length === 0) {
                grid.innerHTML = `
                    <div class="empty-state" style="grid-column: 1/-1;">
                        <h3>No services discovered yet</h3>
                        <p>Run a network scan to discover services</p>
                    </div>
                `;
                return;
            }
            
            for (const [ip, hostInfo] of Object.entries(services)) {
                for (const service of hostInfo.services || []) {
                    const key = `${service.name}_${ip}`;
                    const isConfigured = !!configs[key];
                    const hasData = !!collectedData[key];
                    
                    const card = document.createElement('div');
                    card.className = 'service-card';
                    card.innerHTML = `
                        <div class="service-header">
                            <div>
                                <div class="service-name">${service.name}</div>
                                <div class="service-status">
                                    <span class="status-indicator status-${isConfigured ? 'configured' : 'discovered'}"></span>
                                    <span>${isConfigured ? 'Configured' : 'Discovered'}</span>
                                </div>
                            </div>
                        </div>
                        <div class="service-info">
                            <strong>Host:</strong> ${hostInfo.hostname} (${ip})<br>
                            <strong>Ports:</strong> ${service.ports.join(', ')}<br>
                            <strong>Confidence:</strong> ${(service.confidence * 100).toFixed(0)}%<br>
                            <strong>Type:</strong> ${service.device_type || 'Unknown'}
                        </div>
                        <div class="service-actions">
                            <button class="btn btn-small" onclick="configureService('${service.name}', '${ip}')">
                                ${isConfigured ? '⚙️ Edit Config' : '➕ Configure'}
                            </button>
                            ${isConfigured ? `
                                <button class="btn btn-small btn-secondary" onclick="testService('${service.name}', '${ip}')">
                                    🔗 Test
                                </button>
                            ` : ''}
                        </div>
                    `;
                    grid.appendChild(card);
                }
            }
        }

        async function configureService(serviceName, host) {
            currentService = { name: serviceName, host: host };
            const key = `${serviceName}_${host}`;
            
            document.getElementById('config-title').textContent = `Configure ${serviceName}`;
            
            // Get existing config
            const config = configs[key] || {};
            
            // Build form based on service type
            let formHtml = '';
            
            // Common fields
            formHtml += `
                <div class="form-group">
                    <label>Host</label>
                    <input type="text" id="config-host" value="${host}" readonly>
                </div>
            `;
            
            // Service-specific fields
            if (serviceName.toLowerCase().includes('plex')) {
                formHtml += `
                    <div class="form-group">
                        <label>Plex Token</label>
                        <input type="text" id="config-token" placeholder="Your Plex token" 
                               value="${config.token || ''}">
                    </div>
                `;
            } else if (['radarr', 'sonarr', 'prowlarr', 'bazarr'].some(s => serviceName.toLowerCase().includes(s))) {
                formHtml += `
                    <div class="form-group">
                        <label>API Key</label>
                        <input type="text" id="config-api_key" placeholder="API key from settings" 
                               value="${config.api_key || ''}">
                    </div>
                `;
            } else if (serviceName.toLowerCase().includes('jellyfin')) {
                formHtml += `
                    <div class="form-group">
                        <label>API Key</label>
                        <input type="text" id="config-api_key" placeholder="Jellyfin API key" 
                               value="${config.api_key || ''}">
                    </div>
                `;
            } else if (serviceName.toLowerCase().includes('portainer')) {
                formHtml += `
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" id="config-username" placeholder="Admin username" 
                               value="${config.username || ''}">
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="config-password" placeholder="Admin password" 
                               value="${config.password || ''}">
                    </div>
                `;
            } else {
                // Generic config
                formHtml += `
                    <div class="form-group">
                        <label>Username (if required)</label>
                        <input type="text" id="config-username" placeholder="Username" 
                               value="${config.username || ''}">
                    </div>
                    <div class="form-group">
                        <label>Password (if required)</label>
                        <input type="password" id="config-password" placeholder="Password" 
                               value="${config.password || ''}">
                    </div>
                    <div class="form-group">
                        <label>API Key (if required)</label>
                        <input type="text" id="config-api_key" placeholder="API key" 
                               value="${config.api_key || ''}">
                    </div>
                `;
            }
            
            formHtml += `
                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button class="btn" onclick="saveConfig()">💾 Save</button>
                    <button class="btn btn-secondary" onclick="closeConfigModal()">Cancel</button>
                </div>
            `;
            
            document.getElementById('config-form').innerHTML = formHtml;
            document.getElementById('config-modal').classList.add('active');
        }

        async function saveConfig() {
            if (!currentService) return;
            
            const key = `${currentService.name}_${currentService.host}`;
            const config = { host: currentService.host };
            
            // Collect form values
            const fields = ['token', 'api_key', 'username', 'password'];
            for (const field of fields) {
                const input = document.getElementById(`config-${field}`);
                if (input && input.value) {
                    config[field] = input.value;
                }
            }
            
            try {
                const response = await fetch(
                    `${API_URL}/services/${currentService.name}/${currentService.host}/config`,
                    {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    }
                );
                
                const result = await response.json();
                
                if (response.ok) {
                    configs[key] = config;
                    
                    if (result.data) {
                        collectedData[key] = result.data;
                        showToast('Configuration saved and data collected!', 'success');
                    } else {
                        showToast('Configuration saved!', 'success');
                    }
                    
                    closeConfigModal();
                    updateServiceGrid();
                    updateStats();
                } else {
                    throw new Error(result.error || 'Failed to save configuration');
                }
            } catch (error) {
                showToast('Error: ' + error.message, 'error');
            }
        }

        async function testService(serviceName, host) {
            const key = `${serviceName}_${host}`;
            const config = configs[key];
            
            if (!config) {
                showToast('Please configure the service first', 'error');
                return;
            }
            
            try {
                const response = await fetch(
                    `${API_URL}/services/${serviceName}/${host}/test`,
                    {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    }
                );
                
                const result = await response.json();
                
                if (response.ok) {
                    showToast(`✅ ${result.message}`, 'success');
                } else {
                    showToast(`❌ ${result.message}`, 'error');
                }
            } catch (error) {
                showToast('Connection test failed: ' + error.message, 'error');
            }
        }

        function closeConfigModal() {
            document.getElementById('config-modal').classList.remove('active');
            currentService = null;
        }

        function showGenerateOptions() {
            document.getElementById('generate-modal').classList.add('active');
        }

        function hideGenerateOptions() {
            document.getElementById('generate-modal').classList.remove('active');
        }

        async function generateDocs() {
            const options = {
                network_topology: document.getElementById('opt-network').checked,
                service_dependencies: document.getElementById('opt-dependencies').checked,
                docker_compose: document.getElementById('opt-docker').checked,
                security_audit: document.getElementById('opt-security').checked,
                json: document.getElementById('opt-json').checked,
                html: document.getElementById('opt-html').checked
            };
            
            showToast('Generating documentation...', 'success');
            
            try {
                const response = await fetch(`${API_URL}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ options })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `ladashy_docs_${new Date().toISOString().slice(0, 10)}.zip`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    hideGenerateOptions();
                    showToast('Documentation generated and downloaded!', 'success');
                } else {
                    throw new Error('Generation failed');
                }
            } catch (error) {
                showToast('Failed to generate documentation: ' + error.message, 'error');
            }
        }

        async function saveState() {
            try {
                const response = await fetch(`${API_URL}/state/save`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                showToast('State saved successfully!', 'success');
            } catch (error) {
                showToast('Failed to save state: ' + error.message, 'error');
            }
        }

        async function loadState() {
            try {
                const response = await fetch(`${API_URL}/state/load`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showToast(`State loaded! ${result.services} services found`, 'success');
                    loadServices();
                } else {
                    showToast('No saved state found', 'error');
                }
            } catch (error) {
                showToast('Failed to load state: ' + error.message, 'error');
            }
        }

        function switchTab(tab) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(`tab-${tab}`).classList.add('active');
            
            // Update content based on tab
            if (tab === 'configured') {
                updateConfiguredGrid();
            } else if (tab === 'collected') {
                updateCollectedGrid();
            }
        }

        function updateConfiguredGrid() {
            const grid = document.getElementById('configured-grid');
            grid.innerHTML = '';
            
            let hasConfigured = false;
            
            for (const [ip, hostInfo] of Object.entries(services)) {
                for (const service of hostInfo.services || []) {
                    const key = `${service.name}_${ip}`;
                    if (configs[key]) {
                        hasConfigured = true;
                        const card = createServiceCard(service, hostInfo, ip, true);
                        grid.appendChild(card);
                    }
                }
            }
            
            if (!hasConfigured) {
                grid.innerHTML = `
                    <div class="empty-state" style="grid-column: 1/-1;">
                        <h3>No configured services yet</h3>
                        <p>Configure services from the Discovered tab</p>
                    </div>
                `;
            }
        }

        function updateCollectedGrid() {
            const grid = document.getElementById('collected-grid');
            grid.innerHTML = '';
            
            if (Object.keys(collectedData).length === 0) {
                grid.innerHTML = `
                    <div class="empty-state" style="grid-column: 1/-1;">
                        <h3>No data collected yet</h3>
                        <p>Configure services to collect data</p>
                    </div>
                `;
                return;
            }
            
            for (const [key, data] of Object.entries(collectedData)) {
                const [serviceName, ...hostParts] = key.split('_');
                const host = hostParts.join('_');
                
                const card = document.createElement('div');
                card.className = 'service-card';
                card.innerHTML = `
                    <div class="service-header">
                        <div>
                            <div class="service-name">${serviceName}</div>
                            <div class="service-status">
                                <span class="status-indicator status-configured"></span>
                                <span>Data Available</span>
                            </div>
                        </div>
                    </div>
                    <div class="service-info">
                        <strong>Host:</strong> ${host}<br>
                        <strong>Last Updated:</strong> ${data.last_updated ? new Date(data.last_updated).toLocaleString() : 'Unknown'}<br>
                        ${formatCollectedData(data)}
                    </div>
                `;
                grid.appendChild(card);
            }
        }

        function formatCollectedData(data) {
            let html = '';
            
            // Show key data points
            if (data.version) html += `<strong>Version:</strong> ${data.version}<br>`;
            if (data.libraries) html += `<strong>Libraries:</strong> ${data.libraries.length}<br>`;
            if (data.movies) html += `<strong>Movies:</strong> ${data.movies}<br>`;
            if (data.series) html += `<strong>Series:</strong> ${data.series}<br>`;
            if (data.domains_blocked) html += `<strong>Domains Blocked:</strong> ${data.domains_blocked.toLocaleString()}<br>`;
            if (data.dns_queries_today) html += `<strong>DNS Queries Today:</strong> ${data.dns_queries_today.toLocaleString()}<br>`;
            
            return html;
        }

        function createServiceCard(service, hostInfo, ip, showData = false) {
            const key = `${service.name}_${ip}`;
            const isConfigured = !!configs[key];
            const hasData = !!collectedData[key];
            
            const card = document.createElement('div');
            card.className = 'service-card';
            card.innerHTML = `
                <div class="service-header">
                    <div>
                        <div class="service-name">${service.name}</div>
                        <div class="service-status">
                            <span class="status-indicator status-${isConfigured ? 'configured' : 'discovered'}"></span>
                            <span>${isConfigured ? 'Configured' : 'Discovered'}</span>
                        </div>
                    </div>
                </div>
                <div class="service-info">
                    <strong>Host:</strong> ${hostInfo.hostname} (${ip})<br>
                    <strong>Ports:</strong> ${service.ports.join(', ')}<br>
                    <strong>Confidence:</strong> ${(service.confidence * 100).toFixed(0)}%<br>
                    <strong>Type:</strong> ${service.device_type || 'Unknown'}
                    ${showData && hasData ? '<br>' + formatCollectedData(collectedData[key]) : ''}
                </div>
                <div class="service-actions">
                    <button class="btn btn-small" onclick="configureService('${service.name}', '${ip}')">
                        ${isConfigured ? '⚙️ Edit Config' : '➕ Configure'}
                    </button>
                    ${isConfigured ? `
                        <button class="btn btn-small btn-secondary" onclick="testService('${service.name}', '${ip}')">
                            🔗 Test
                        </button>
                    ` : ''}
                </div>
            `;
            return card;
        }

        function updateStats() {
            let totalServices = 0;
            let configuredCount = 0;
            
            for (const [ip, hostInfo] of Object.entries(services)) {
                for (const service of hostInfo.services || []) {
                    totalServices++;
                    const key = `${service.name}_${ip}`;
                    if (configs[key]) configuredCount++;
                }
            }
            
            document.getElementById('stat-hosts').textContent = Object.keys(services).length;
            document.getElementById('stat-services').textContent = totalServices;
            document.getElementById('stat-configured').textContent = configuredCount;
            document.getElementById('stat-collected').textContent = Object.keys(collectedData).length;
        }

        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            const toastMessage = document.getElementById('toast-message');
            
            toast.className = `toast ${type} show`;
            toastMessage.textContent = message;
            
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }

        function showServiceDefinitions() {
            // This would show available service definitions
            showToast('Service definitions feature coming soon!', 'success');
        }

        // Initialize on load
        window.addEventListener('load', () => {
            loadServices();
        });

        // Handle modal clicks
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('active');
            }
        });
    </script>
</body>
</html>
EOFHTML

# Install dependencies
echo "📦 Installing dependencies..."
pip install flask flask-cors

# Create run script
cat > ladashy_unified/run.sh << 'EOFRUN'
#!/bin/bash
# Run LaDashy Web Interface

echo "🚀 Starting LaDashy Web Interface..."
echo ""

# Kill any existing processes on our ports
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Start API server
cd backend
python api.py &
API_PID=$!
cd ..

# Give API time to start
sleep 2

# Start web server
cd frontend
python -m http.server 8080 &
WEB_PID=$!
cd ..

echo ""
echo "✅ LaDashy is running!"
echo ""
echo "🌐 Open your browser to: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup function
cleanup() {
    echo -e "\nStopping LaDashy..."
    kill $API_PID $WEB_PID 2>/dev/null
    exit 0
}

trap cleanup INT

# Wait
wait
EOFRUN

chmod +x ladashy_unified/run.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📦 Dependencies installed"
echo "🔧 All features integrated"
echo "🚀 Auto-launching LaDashy Web Interface..."
echo ""

# Auto-launch
cd ladashy_unified
./run.sh
