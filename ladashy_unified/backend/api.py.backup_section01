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

from flask import send_from_directory
import os

# Add route for serving icons

@app.route('/icons/<path:filename>')
def serve_icon(filename):
    icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons')
    return send_from_directory(icons_dir, filename)

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
            collector = manager.get_collector(service_name.lower(), config)
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
    collector = manager.get_collector(service_name.lower(), config)
    
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
