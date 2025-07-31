import sys
sys.path.insert(0, '.')

# Read the current scanner
with open('homelab_wizard/core/scanner.py', 'r') as f:
    content = f.read()

# Define the new discover_all_services method
new_method = '''
    def discover_all_services(self, progress_callback=None) -> Dict[str, List[Dict]]:
        """Discover all services on all networks with comprehensive port scanning"""
        all_services = {}
        
        # First, find all hosts
        hosts = self.scan_networks(progress_callback)
        
        # Import what we need
        from ..services.definitions import get_all_services
        all_service_definitions = get_all_services()
        
        # Then scan each host for services
        for ip, hostname in hosts.items():
            if progress_callback:
                progress_callback(f"Deep scanning {ip} ({hostname})")
            
            # Comprehensive port list
            ports_to_check = [
                # Web services
                80, 443, 8080, 8443, 8081, 8090, 8000, 3000, 5000, 5001,
                # Media services
                32400,  # Plex
                8096,   # Jellyfin/Emby
                7878,   # Radarr
                8989,   # Sonarr
                9696,   # Prowlarr
                6767,   # Bazarr
                8686,   # Lidarr
                8787,   # Readarr
                8181,   # Tautulli
                5055,   # Overseerr
                3579,   # Ombi
                # Download clients
                8112,   # Deluge
                9091,   # Transmission
                6881,   # qBittorrent
                # Management
                9000,   # Portainer
                9090,   # Cockpit/Prometheus
                81,     # Nginx Proxy Manager
                # Network services
                53, 22, 21, 445,
                # Databases
                3306, 5432, 27017, 6379,
            ]
            
            # Find open ports
            open_ports = []
            for port in ports_to_check:
                if self._is_port_open(ip, port):
                    open_ports.append(port)
                    if progress_callback:
                        progress_callback(f"Found open port {port} on {ip}")
            
            if not open_ports:
                continue
            
            # Try smart detection if available
            detected_services = {}
            try:
                from .service_detector import ServiceDetector
                detector = ServiceDetector()
                
                for port in open_ports:
                    service_name, confidence = detector.identify_service(ip, port)
                    if service_name:
                        detected_services[port] = (service_name, confidence)
            except:
                pass
            
            # Match services based on ports
            found_services = []
            
            # Check each service definition
            for service_def in all_service_definitions:
                service_ports = service_def.get("ports", [])
                matched_ports = [p for p in service_ports if p in open_ports]
                
                if matched_ports:
                    # Calculate confidence
                    confidence = 0.6  # Base confidence from port match
                    
                    # Check if smart detection agrees
                    for port in matched_ports:
                        if port in detected_services:
                            detected_name, detected_conf = detected_services[port]
                            if service_def["name"].lower() in detected_name.lower():
                                confidence = max(confidence, detected_conf)
                    
                    found_services.append({
                        "name": service_def["name"],
                        "host": ip,
                        "ports": matched_ports,
                        "description": service_def.get("description", ""),
                        "confidence": confidence,
                        "device_type": "docker" if hostname == "Unknown" else "host"
                    })
            
            # Add any services detected but not in our definitions
            for port, (service_name, confidence) in detected_services.items():
                # Check if we already added this service
                already_added = any(
                    service_name.lower() in s["name"].lower() 
                    for s in found_services
                )
                if not already_added and confidence > 0.7:
                    found_services.append({
                        "name": service_name.replace('_', ' ').title(),
                        "host": ip,
                        "ports": [port],
                        "confidence": confidence,
                        "device_type": "detected"
                    })
            
            if found_services:
                all_services[ip] = {
                    "hostname": hostname,
                    "services": found_services
                }
        
        return all_services

    def _is_port_open(self, host: str, port: int) -> bool:
        """Quick check if port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)  # Very fast timeout
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
'''

# Replace the old method
if 'def discover_all_services' in content:
    # Find where the method starts
    start = content.find('def discover_all_services')
    # Find the next method
    next_method = content.find('\n    def ', start + 1)
    if next_method == -1:
        # No next method, so look for class end
        next_method = content.find('\nclass ', start)
        if next_method == -1:
            next_method = len(content)
    
    # Extract the indentation
    indent_start = content.rfind('\n', 0, start) + 1
    indent = content[indent_start:start]
    
    # Replace the method
    content = content[:start] + new_method.strip() + '\n\n' + indent + content[next_method:]

# Make sure _is_port_open is there
if 'def _is_port_open' not in content:
    # Add it before the last method or at the end of the class
    class_end = content.rfind('\n\nclass')
    if class_end == -1:
        class_end = len(content)
    content = content[:class_end] + '''

    def _is_port_open(self, host: str, port: int) -> bool:
        """Quick check if port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)  # Very fast timeout
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
''' + content[class_end:]

# Save back
with open('homelab_wizard/core/scanner.py', 'w') as f:
    f.write(content)

print("Scanner completely updated with better service discovery!")
