import urllib3
import warnings

import urllib3
import warnings

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
Network scanner for service discovery
"""
import socket
import subprocess
import platform
import ipaddress
import threading
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from .service_detector import ServiceDetector

class NetworkScanner:
    def __init__(self):
        self.networks = ["192.168.1.0/24"]  # Default network
        self.discovered_hosts = []
        self.scan_timeout = 1
        self.max_threads = 50
        
    def add_network(self, network: str) -> bool:
        """Add a network to scan list"""
        try:
            # Validate network format
            ipaddress.ip_network(network)
            if network not in self.networks:
                self.networks.append(network)
            return True
        except ValueError:
            return False
    
    def remove_network(self, network: str):
        """Remove a network from scan list"""
        if network in self.networks:
            self.networks.remove(network)
    
    def get_networks(self) -> List[str]:
        """Get list of networks to scan"""
        return self.networks.copy()
    
    def scan_networks(self, progress_callback=None) -> Dict[str, str]:
        """Scan all configured networks for active hosts"""
        all_hosts = {}
        
        for network in self.networks:
            if progress_callback:
                progress_callback(f"Scanning network: {network}")
            
            hosts = self._scan_network(network, progress_callback)
            all_hosts.update(hosts)
            
        return all_hosts
    
    def _scan_network(self, network: str, progress_callback=None) -> Dict[str, str]:
        """Scan a specific network"""
        hosts = {}
        
        try:
            net = ipaddress.ip_network(network)
            total_hosts = sum(1 for _ in net.hosts())
            
            if progress_callback:
                progress_callback(f"Scanning {total_hosts} hosts in {network}")
            
            # Use thread pool for parallel scanning
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                # Submit all ping tasks
                future_to_ip = {
                    executor.submit(self._check_host, str(ip)): str(ip) 
                    for ip in net.hosts()
                }
                
                # Process results as they complete
                completed = 0
                for future in as_completed(future_to_ip):
                    ip = future_to_ip[future]
                    completed += 1
                    
                    if progress_callback and completed % 10 == 0:
                        progress_callback(f"Progress: {completed}/{total_hosts} hosts")
                    
                    try:
                        hostname = future.result()
                        if hostname:
                            hosts[ip] = hostname
                            if progress_callback:
                                progress_callback(f"Found: {ip} ({hostname})")
                    except Exception as e:
                        pass
                        
        except ValueError as e:
            if progress_callback:
                progress_callback(f"Invalid network: {network}")
                
        return hosts
    
    def _check_host(self, ip: str) -> str:
        """Check if host is alive and get hostname"""
        if self._ping_host(ip):
            # Try to get hostname
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                return hostname
            except:
                return "Unknown"
        return None
    
    def _ping_host(self, ip: str) -> bool:
        """Check if host is reachable"""
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", "-W", str(self.scan_timeout), ip]
        
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                timeout=self.scan_timeout + 0.5
            )
            return result.returncode == 0
        except:
            return False
    
    def scan_host_services(self, host: str, progress_callback=None) -> List[Dict]:
        """Scan a specific host for services"""
        from ..services.definitions import get_all_services
        
        discovered_services = []
        all_services = get_all_services()
        
        if progress_callback:
            progress_callback(f"Scanning services on {host}")
        
        # Check each service
        for service in all_services:
            if progress_callback:
                progress_callback(f"Checking {service['name']} on {host}")
            
            # Check if service ports are open
            open_ports = self.scan_ports(host, service["ports"])
            if open_ports:
                discovered_services.append({
                    "name": service["name"],
                    "host": host,
                    "ports": open_ports,
                    "description": service["description"]
                })
                
        return discovered_services
    
    def scan_ports(self, host: str, ports: List[int]) -> List[int]:
        """Scan specific ports on a host"""
        open_ports = []
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            
            try:
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
            except:
                pass
            finally:
                sock.close()
                
        return open_ports
    
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

    