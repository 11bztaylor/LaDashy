# Quick patch to update the scanner
import sys
sys.path.insert(0, '.')

# Read the current scanner
with open('homelab_wizard/core/scanner.py', 'r') as f:
    content = f.read()

# Add the import for service detector at the top
if 'from .service_detector import ServiceDetector' not in content:
    imports = """import socket
import subprocess
import platform
import ipaddress
import threading
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from .service_detector import ServiceDetector"""
    
    content = content.replace(
        """import socket
import subprocess
import platform
import ipaddress
import threading
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed""",
        imports
    )

# Update the discover_all_services method to use smart detection
new_method = '''
    def discover_all_services(self, progress_callback=None) -> Dict[str, List[Dict]]:
        """Discover all services on all networks with smart detection"""
        all_services = {}
        detector = ServiceDetector()
        
        # First, find all hosts
        hosts = self.scan_networks(progress_callback)
        
        # Then scan each host for services
        for ip, hostname in hosts.items():
            if progress_callback:
                progress_callback(f"Scanning services on {ip} ({hostname})")
            
            # Get all open ports
            common_ports = [
                22, 53, 80, 81, 443, 445, 631, 3306, 5432, 6379,
                7878, 8080, 8081, 8096, 8123, 8443, 8989, 9000, 9090,
                9696, 32400
            ]
            
            open_ports = []
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                if sock.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
                sock.close()
            
            # Check if it's a router first
            router_type, router_conf = detector.identify_router(ip, open_ports)
            if router_type and router_conf > 0.8:
                # It's a router, only add router service
                all_services[ip] = {
                    "hostname": hostname,
                    "services": [{
                        "name": router_type.replace('_', ' ').title(),
                        "host": ip,
                        "ports": open_ports,
                        "confidence": router_conf,
                        "device_type": "router"
                    }]
                }
                continue
            
            # Not a router, identify services
            services = []
            for port in open_ports:
                if progress_callback:
                    progress_callback(f"Identifying service on {ip}:{port}")
                
                service_name, confidence = detector.identify_service_smart(
                    ip, port, open_ports, hostname
                )
                
                if service_name and confidence > 0.5:
                    # Check if we already have this service
                    existing = next((s for s in services if s["name"] == service_name), None)
                    if existing:
                        existing["ports"].append(port)
                    else:
                        services.append({
                            "name": service_name.replace('_', ' ').title(),
                            "host": ip,
                            "ports": [port],
                            "confidence": confidence,
                            "device_type": "docker" if detector.is_docker_container(ip, hostname) else "host"
                        })
            
            if services:
                all_services[ip] = {
                    "hostname": hostname,
                    "services": services
                }
        
        return all_services
'''

# Replace the old method
if 'def discover_all_services' in content:
    # Find the method and replace it
    start = content.find('def discover_all_services')
    # Find the next method definition
    next_def = content.find('\n    def ', start + 1)
    if next_def == -1:
        next_def = len(content)
    
    # Replace the method
    content = content[:start] + new_method.strip() + '\n\n    ' + content[next_def:]

# Save the updated file
with open('homelab_wizard/core/scanner.py', 'w') as f:
    f.write(content)

print("Scanner updated!")
