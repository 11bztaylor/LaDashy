# Add these improvements to scanner.py

def scan_host_services(self, host: str, progress_callback=None) -> List[Dict]:
    """Scan a specific host for services with better detection"""
    from ..services.definitions import get_all_services
    
    discovered_services = []
    all_services = get_all_services()
    
    if progress_callback:
        progress_callback(f"Deep scanning {host}")
    
    # Extended port list - all common service ports
    extended_ports = [
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
        # Home automation
        8123,   # Home Assistant
        1880,   # Node-RED
        # Monitoring
        3001,   # Uptime Kuma
        19999,  # Netdata
        8086,   # InfluxDB
        # Network services
        53,     # DNS
        22,     # SSH
        21,     # FTP
        25,     # SMTP
        110,    # POP3
        143,    # IMAP
        445,    # SMB
        3389,   # RDP
        # Databases
        3306,   # MySQL/MariaDB
        5432,   # PostgreSQL
        27017,  # MongoDB
        6379,   # Redis
        # Other
        8384,   # Syncthing
        2342,   # PhotoPrism
        8200,   # Duplicati
        10000,  # Webmin
    ]
    
    # Quick scan to find open ports
    open_ports = []
    for port in extended_ports:
        if self._is_port_open(host, port):
            open_ports.append(port)
            if progress_callback:
                progress_callback(f"Found open port {port} on {host}")
    
    # Try to identify services on open ports
    try:
        from .service_detector import ServiceDetector
        detector = ServiceDetector()
        
        # First check if it's a router
        router_type, router_conf = detector.identify_router(host, open_ports)
        if router_type and router_conf > 0.8:
            # It's a router, add it but continue scanning for other services
            discovered_services.append({
                "name": router_type.replace('_', ' ').title(),
                "host": host,
                "ports": [p for p in open_ports if p in [80, 443, 8443]],
                "confidence": router_conf,
                "device_type": "router"
            })
            # Don't count port 53 as a separate service on routers
            open_ports = [p for p in open_ports if p != 53]
    except:
        pass
    
    # Check each service definition against open ports
    for service in all_services:
        service_ports = service.get("ports", [])
        matched_ports = [p for p in service_ports if p in open_ports]
        
        if matched_ports:
            # Try smart detection first
            confidence = 0.5  # Base confidence from port match
            
            try:
                from .service_detector import ServiceDetector
                detector = ServiceDetector()
                
                for port in matched_ports:
                    detected_name, detected_conf = detector.identify_service(host, port)
                    if detected_name and service["name"].lower() in detected_name.lower():
                        confidence = max(confidence, detected_conf)
                    elif detected_name:
                        # Different service detected on this port
                        continue
            except:
                pass
            
            # Add service if we have a match
            if matched_ports:
                discovered_services.append({
                    "name": service["name"],
                    "host": host,
                    "ports": matched_ports,
                    "description": service.get("description", ""),
                    "confidence": confidence,
                    "device_type": "service"
                })
    
    return discovered_services

def _is_port_open(self, host: str, port: int) -> bool:
    """Quick check if port is open with short timeout"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)  # Very short timeout for speed
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def discover_all_services(self, progress_callback=None) -> Dict[str, List[Dict]]:
    """Discover all services on all networks - improved version"""
    all_services = {}
    
    # First, find all hosts
    hosts = self.scan_networks(progress_callback)
    
    # Then scan each host for services
    for ip, hostname in hosts.items():
        if progress_callback:
            progress_callback(f"Scanning services on {ip} ({hostname})")
        
        # Use the improved service scanner
        services = self.scan_host_services(ip, progress_callback)
        
        if services:
            all_services[ip] = {
                "hostname": hostname,
                "services": services
            }
    
    return all_services
