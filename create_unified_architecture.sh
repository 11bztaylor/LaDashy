#!/bin/bash
# Create unified LaDashy architecture

echo "=== Creating Unified LaDashy Architecture ==="

# Create new directory structure
mkdir -p ladashy_unified/{backend,frontend,docker,desktop,shared}

# Create shared core library
cat > ladashy_unified/shared/core.py << 'EOFCORE'
"""
LaDashy Core Library
Shared functionality for all deployment methods
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceInfo:
    name: str
    host: str
    ports: List[int]
    confidence: float = 1.0
    device_type: str = "unknown"
    
@dataclass
class HostInfo:
    hostname: str
    ip: str
    services: List[ServiceInfo]

class LaDashyCore:
    """Core functionality shared across all interfaces"""
    
    def __init__(self):
        self.discovered_services: Dict[str, HostInfo] = {}
        self.service_configs: Dict[str, Dict] = {}
        self.collected_data: Dict[str, Dict] = {}
        
    def scan_network(self, networks: List[str], progress_callback=None):
        """Scan network for services"""
        # Import here to avoid circular dependencies
        from homelab_wizard.core.scanner import NetworkScanner
        
        scanner = NetworkScanner()
        for network in networks:
            scanner.add_network(network)
            
        raw_services = scanner.discover_all_services(progress_callback)
        
        # Convert to our data structure
        self.discovered_services = {}
        for ip, data in raw_services.items():
            services = []
            for svc in data.get('services', []):
                services.append(ServiceInfo(
                    name=svc['name'],
                    host=ip,
                    ports=svc.get('ports', []),
                    confidence=svc.get('confidence', 1.0),
                    device_type=svc.get('device_type', 'unknown')
                ))
            
            self.discovered_services[ip] = HostInfo(
                hostname=data.get('hostname', 'Unknown'),
                ip=ip,
                services=services
            )
        
        return self.discovered_services
    
    def generate_documentation(self, output_dir: str, options: Dict[str, bool]):
        """Generate documentation"""
        from homelab_wizard.generators.documentation_generator import DocumentationGenerator
        
        # Convert back to expected format
        services_dict = {}
        for ip, host_info in self.discovered_services.items():
            services_dict[ip] = {
                'hostname': host_info.hostname,
                'services': [
                    {
                        'name': s.name,
                        'ports': s.ports,
                        'confidence': s.confidence,
                        'device_type': s.device_type
                    }
                    for s in host_info.services
                ]
            }
        
        generator = DocumentationGenerator(output_dir)
        results = generator.generate_all(
            services_dict,
            self.service_configs,
            self.collected_data
        )
        
        # Generate additional formats based on options
        if options.get('json', True):
            generator.export_to_json(services_dict, self.service_configs, self.collected_data)
        if options.get('html', True):
            generator.export_to_html_dashboard(services_dict, self.service_configs)
            
        return results
    
    def collect_service_data(self, service_name: str, host: str, config: Dict):
        """Collect data from a specific service"""
        from homelab_wizard.collectors.manager import CollectorManager
        
        manager = CollectorManager()
        collector = manager.get_collector(service_name)
        
        if collector:
            port = next((s.ports[0] for s in self.discovered_services[host].services 
                        if s.name == service_name), 8080)
            
            if collector.test_connection(host, port, config):
                basic_info = collector.collect_basic_info(host, port, config)
                detailed_info = collector.collect_detailed_info(host, port, config)
                
                service_key = f"{service_name}_{host}"
                self.collected_data[service_key] = {
                    **basic_info,
                    **detailed_info
                }
                return True
        return False
    
    def save_state(self, filepath: str):
        """Save current state to file"""
        state = {
            'discovered_services': {
                ip: {
                    'hostname': info.hostname,
                    'services': [
                        {
                            'name': s.name,
                            'ports': s.ports,
                            'confidence': s.confidence,
                            'device_type': s.device_type
                        }
                        for s in info.services
                    ]
                }
                for ip, info in self.discovered_services.items()
            },
            'service_configs': self.service_configs,
            'collected_data': self.collected_data,
            'timestamp': datetime.now().isoformat()
        }
        
        Path(filepath).write_text(json.dumps(state, indent=2))
    
    def load_state(self, filepath: str):
        """Load state from file"""
        if Path(filepath).exists():
            state = json.loads(Path(filepath).read_text())
            
            # Restore discovered services
            self.discovered_services = {}
            for ip, data in state.get('discovered_services', {}).items():
                services = []
                for svc in data.get('services', []):
                    services.append(ServiceInfo(
                        name=svc['name'],
                        host=ip,
                        ports=svc.get('ports', []),
                        confidence=svc.get('confidence', 1.0),
                        device_type=svc.get('device_type', 'unknown')
                    ))
                
                self.discovered_services[ip] = HostInfo(
                    hostname=data.get('hostname', 'Unknown'),
                    ip=ip,
                    services=services
                )
            
            self.service_configs = state.get('service_configs', {})
            self.collected_data = state.get('collected_data', {})
            return True
        return False
EOFCORE

# Create REST API backend
cat > ladashy_unified/backend/api.py << 'EOFAPI'
"""
LaDashy REST API
Backend service that can be used by any frontend
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import tempfile
import zipfile
from pathlib import Path
import threading

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.core import LaDashyCore

app = Flask(__name__)
CORS(app)

# Global core instance
core = LaDashyCore()
scan_status = {"scanning": False, "progress": "", "error": None}

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route('/api/scan', methods=['POST'])
def scan_network():
    """Start network scan"""
    if scan_status["scanning"]:
        return jsonify({"error": "Scan already in progress"}), 400
    
    data = request.json
    networks = data.get('networks', ['192.168.1.0/24'])
    
    def scan_worker():
        scan_status["scanning"] = True
        scan_status["error"] = None
        try:
            def progress_callback(msg):
                scan_status["progress"] = msg
            
            core.scan_network(networks, progress_callback)
            scan_status["progress"] = "Scan complete"
        except Exception as e:
            scan_status["error"] = str(e)
        finally:
            scan_status["scanning"] = False
    
    thread = threading.Thread(target=scan_worker, daemon=True)
    thread.start()
    
    return jsonify({"status": "Scan started", "networks": networks})

@app.route('/api/scan/status')
def get_scan_status():
    """Get scan status"""
    return jsonify({
        "scanning": scan_status["scanning"],
        "progress": scan_status["progress"],
        "error": scan_status["error"],
        "services_found": sum(len(h.services) for h in core.discovered_services.values())
    })

@app.route('/api/services')
def get_services():
    """Get discovered services"""
    services = {}
    for ip, host_info in core.discovered_services.items():
        services[ip] = {
            'hostname': host_info.hostname,
            'services': [
                {
                    'name': s.name,
                    'ports': s.ports,
                    'confidence': s.confidence,
                    'device_type': s.device_type
                }
                for s in host_info.services
            ]
        }
    return jsonify(services)

@app.route('/api/services/<service_name>/<host>/config', methods=['GET', 'POST'])
def service_config(service_name, host):
    """Get or update service configuration"""
    service_key = f"{service_name}_{host}"
    
    if request.method == 'GET':
        return jsonify(core.service_configs.get(service_key, {}))
    else:
        core.service_configs[service_key] = request.json
        return jsonify({"status": "Configuration updated"})

@app.route('/api/services/<service_name>/<host>/collect', methods=['POST'])
def collect_service_data(service_name, host):
    """Collect data from a service"""
    config = request.json
    service_key = f"{service_name}_{host}"
    
    if core.collect_service_data(service_name, host, config):
        return jsonify({
            "status": "Data collected",
            "data": core.collected_data.get(service_key, {})
        })
    else:
        return jsonify({"error": "Failed to collect data"}), 500

@app.route('/api/generate', methods=['POST'])
def generate_documentation():
    """Generate documentation"""
    data = request.json
    options = data.get('options', {
        'network_topology': True,
        'service_dependencies': True,
        'docker_compose': True,
        'security_audit': True,
        'json': True,
        'html': True
    })
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate documentation
        core.generate_documentation(temp_dir, options)
        
        # Create zip file
        zip_path = Path(temp_dir) / "ladashy_docs.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file != "ladashy_docs.zip":
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"ladashy_docs_{core.discovered_services.get('timestamp', 'latest')}.zip"
        )

@app.route('/api/state', methods=['GET', 'POST'])
def manage_state():
    """Save or load application state"""
    if request.method == 'GET':
        # Return current state
        return jsonify({
            'discovered_services': len(core.discovered_services),
            'configured_services': len(core.service_configs),
            'collected_data': len(core.collected_data)
        })
    else:
        # Save state
        state_file = '/tmp/ladashy_state.json'
        core.save_state(state_file)
        return jsonify({"status": "State saved", "file": state_file})

if __name__ == '__main__':
    # Check if we should load existing services from parent directory
    parent_path = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(parent_path))
    
    app.run(host='0.0.0.0', port=5000, debug=True)
EOFAPI

# Create web frontend
cat > ladashy_unified/frontend/index.html << 'EOFHTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LaDashy - Homelab Documentation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .header h1 {
            color: #4ecdc4;
            margin-bottom: 10px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .stat-card h3 {
            color: #96ceb4;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #4ecdc4;
        }
        .controls {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .btn {
            background: #4ecdc4;
            color: #1a1a1a;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 10px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #45b7d1;
            transform: translateY(-2px);
        }
        .btn:disabled {
            background: #555;
            cursor: not-allowed;
            transform: none;
        }
        .services {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .service-card {
            background: #3d3d3d;
            padding: 15px;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .service-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        .service-name {
            color: #4ecdc4;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .service-info {
            font-size: 0.9em;
            color: #b0b0b0;
        }
        .progress {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        .progress.active { display: block; }
        .progress-bar {
            background: #3d3d3d;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            background: #4ecdc4;
            height: 100%;
            width: 0%;
            transition: width 0.3s;
        }
        .options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .option {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .option input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        .network-input {
            background: #3d3d3d;
            border: 1px solid #555;
            color: #e0e0e0;
            padding: 10px;
            border-radius: 5px;
            width: 100%;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 LaDashy</h1>
            <p>Homelab Documentation Generator</p>
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
        </div>

        <div class="controls">
            <h2>Network Scanner</h2>
            <div style="margin: 20px 0;">
                <label>Network Range:</label>
                <input type="text" id="network-range" class="network-input" 
                       value="192.168.1.0/24" placeholder="192.168.1.0/24">
            </div>
            <button class="btn" id="btn-scan" onclick="startScan()">
                🔍 Scan Network
            </button>
            <button class="btn" id="btn-generate" onclick="showGenerateOptions()" disabled>
                📄 Generate Documentation
            </button>
        </div>

        <div class="progress" id="progress">
            <div id="progress-text">Initializing scan...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
        </div>

        <div class="services" id="services" style="display: none;">
            <h2>Discovered Services</h2>
            <div class="service-grid" id="service-grid"></div>
        </div>

        <div class="controls" id="generate-options" style="display: none;">
            <h2>Documentation Options</h2>
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
            <button class="btn" onclick="generateDocs()">
                🚀 Generate & Download
            </button>
            <button class="btn" onclick="hideGenerateOptions()">
                ❌ Cancel
            </button>
        </div>
    </div>

    <script>
        const API_URL = window.location.protocol + '//' + window.location.hostname + ':5000/api';
        let scanInterval = null;

        async function startScan() {
            const networks = document.getElementById('network-range').value.split(',').map(n => n.trim());
            
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
                    // Start polling for status
                    scanInterval = setInterval(checkScanStatus, 1000);
                }
            } catch (error) {
                alert('Failed to start scan: ' + error.message);
                document.getElementById('btn-scan').disabled = false;
                document.getElementById('progress').classList.remove('active');
            }
        }

        async function checkScanStatus() {
            try {
                const response = await fetch(`${API_URL}/scan/status`);
                const status = await response.json();
                
                document.getElementById('progress-text').textContent = status.progress || 'Scanning...';
                
                if (!status.scanning) {
                    clearInterval(scanInterval);
                    document.getElementById('btn-scan').disabled = false;
                    document.getElementById('progress').classList.remove('active');
                    
                    if (status.error) {
                        alert('Scan error: ' + status.error);
                    } else {
                        loadServices();
                    }
                }
                
                // Update stats
                document.getElementById('stat-services').textContent = status.services_found || 0;
            } catch (error) {
                console.error('Status check error:', error);
            }
        }

        async function loadServices() {
            try {
                const response = await fetch(`${API_URL}/services`);
                const services = await response.json();
                
                const grid = document.getElementById('service-grid');
                grid.innerHTML = '';
                
                let totalServices = 0;
                let hosts = 0;
                
                for (const [ip, hostInfo] of Object.entries(services)) {
                    hosts++;
                    for (const service of hostInfo.services) {
                        totalServices++;
                        
                        const card = document.createElement('div');
                        card.className = 'service-card';
                        card.innerHTML = `
                            <div class="service-name">${service.name}</div>
                            <div class="service-info">
                                <strong>Host:</strong> ${hostInfo.hostname} (${ip})<br>
                                <strong>Ports:</strong> ${service.ports.join(', ')}<br>
                                <strong>Confidence:</strong> ${(service.confidence * 100).toFixed(0)}%
                            </div>
                        `;
                        grid.appendChild(card);
                    }
                }
                
                document.getElementById('stat-hosts').textContent = hosts;
                document.getElementById('stat-services').textContent = totalServices;
                document.getElementById('services').style.display = 'block';
                document.getElementById('btn-generate').disabled = totalServices === 0;
            } catch (error) {
                console.error('Failed to load services:', error);
            }
        }

        function showGenerateOptions() {
            document.getElementById('generate-options').style.display = 'block';
        }

        function hideGenerateOptions() {
            document.getElementById('generate-options').style.display = 'none';
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
            
            try {
                const response = await fetch(`${API_URL}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ options })
                });
                
                if (response.ok) {
                    // Download the file
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'ladashy_docs.zip';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    hideGenerateOptions();
                    alert('Documentation generated and downloaded!');
                }
            } catch (error) {
                alert('Failed to generate documentation: ' + error.message);
            }
        }

        // Load initial state
        loadServices();
    </script>
</body>
</html>
EOFHTML

# Create Dockerfile for web version
cat > ladashy_unified/docker/Dockerfile << 'EOFDOCKER'
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app/

# Expose port
EXPOSE 5000

# Run the API
CMD ["python", "backend/api.py"]
EOFDOCKER

# Create docker-compose.yml
cat > ladashy_unified/docker/docker-compose.yml << 'EOFCOMPOSE'
version: '3.8'

services:
  ladashy:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: ladashy
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
    networks:
      - homelab
    restart: unless-stopped

  ladashy-frontend:
    image: nginx:alpine
    container_name: ladashy-frontend
    ports:
      - "8080:80"
    volumes:
      - ../frontend:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - ladashy
    networks:
      - homelab
    restart: unless-stopped

networks:
  homelab:
    driver: bridge
EOFCOMPOSE

# Create nginx config
cat > ladashy_unified/docker/nginx.conf << 'EOFNGINX'
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://ladashy:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOFNGINX

# Create desktop wrapper (Electron-based)
cat > ladashy_unified/desktop/main.js << 'EOFELECTRON'
const { app, BrowserWindow, Menu, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let apiProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        },
        icon: path.join(__dirname, 'icon.png'),
        title: 'LaDashy - Homelab Documentation'
    });

    // Start the API server
    apiProcess = spawn('python', [path.join(__dirname, '../backend/api.py')]);
    
    apiProcess.stdout.on('data', (data) => {
        console.log(`API: ${data}`);
    });

    // Wait a moment for the server to start
    setTimeout(() => {
        mainWindow.loadURL('http://localhost:5000');
    }, 2000);

    mainWindow.on('closed', () => {
        mainWindow = null;
        if (apiProcess) {
            apiProcess.kill();
        }
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});
EOFELECTRON

# Create package.json for desktop app
cat > ladashy_unified/desktop/package.json << 'EOFPACKAGE'
{
  "name": "ladashy-desktop",
  "version": "1.0.0",
  "description": "LaDashy Desktop Application",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build-win": "electron-builder --win",
    "build-mac": "electron-builder --mac",
    "build-linux": "electron-builder --linux"
  },
  "devDependencies": {
    "electron": "^27.0.0",
    "electron-builder": "^24.0.0"
  },
  "build": {
    "appId": "com.ladashy.app",
    "productName": "LaDashy",
    "directories": {
      "output": "dist"
    },
    "win": {
      "target": "nsis"
    },
    "mac": {
      "target": "dmg"
    },
    "linux": {
      "target": "AppImage"
    }
  }
}
EOFPACKAGE

# Create unified requirements.txt
cat > ladashy_unified/requirements.txt << 'EOFREQ'
# Web Framework
flask==3.0.0
flask-cors==4.0.0

# Existing dependencies
requests==2.31.0
paramiko==3.4.0
jinja2==3.1.2
markdown==3.5.1
pyyaml==6.0.1

# For desktop UI (optional)
customtkinter==5.2.1
pillow==10.2.0
EOFREQ

# Create launch script
cat > ladashy_unified/launch.py << 'EOFLAUNCH'
#!/usr/bin/env python3
"""
LaDashy Universal Launcher
Detects platform and launches appropriate interface
"""
import sys
import os
import platform
import subprocess

def launch_web():
    """Launch web interface"""
    print("Starting LaDashy Web Interface...")
    subprocess.run([sys.executable, "backend/api.py"])

def launch_desktop():
    """Launch desktop interface"""
    system = platform.system()
    
    if system == "Windows":
        print("Starting LaDashy Desktop (Windows)...")
        # Add the parent directory to Python path for imports
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        from homelab_wizard.gui.modern_main_window import ModernHomelabWizard
        app = ModernHomelabWizard()
        app.run()
    else:
        # For Mac/Linux, could use Electron or native
        print("Starting LaDashy Web Interface (Mac/Linux)...")
        launch_web()

def launch_docker():
    """Build and run Docker version"""
    print("Building LaDashy Docker container...")
    os.chdir("docker")
    subprocess.run(["docker-compose", "up", "--build"])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "web":
            launch_web()
        elif mode == "desktop":
            launch_desktop()
        elif mode == "docker":
            launch_docker()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python launch.py [web|desktop|docker]")
    else:
        # Auto-detect best mode
        if os.path.exists("/.dockerenv"):
            print("Running in Docker container")
            launch_web()
        elif platform.system() == "Windows":
            launch_desktop()
        else:
            launch_web()
EOFLAUNCH

chmod +x launch.py

echo "✅ Unified LaDashy architecture created!"
echo ""
echo "Directory structure:"
echo "  ladashy_unified/"
echo "    ├── shared/       # Core library used by all interfaces"
echo "    ├── backend/      # REST API (Flask)"
echo "    ├── frontend/     # Web UI (HTML/JS)"
echo "    ├── desktop/      # Desktop app (Electron wrapper)"
echo "    └── docker/       # Docker configuration"
echo ""
echo "To use:"
echo "  cd ladashy_unified"
echo "  python launch.py web      # Web interface"
echo "  python launch.py desktop  # Desktop app"
echo "  python launch.py docker   # Docker container"
