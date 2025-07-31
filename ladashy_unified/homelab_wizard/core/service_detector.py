"""
Advanced service detection with multiple identification methods
"""
import socket
import requests
import json
from typing import Dict, List, Optional, Tuple

class ServiceDetector:
    def __init__(self):
        self.timeout = 2
        
    def identify_service(self, host: str, port: int) -> Tuple[str, float]:
        """
        Identify service on host:port
        Returns: (service_name, confidence_score)
        """
        # Try multiple detection methods
        methods = [
            self._check_http_response,
            self._check_banner,
            self._check_specific_endpoints,
        ]
        
        results = []
        for method in methods:
            try:
                service, confidence = method(host, port)
                if service:
                    results.append((service, confidence))
            except:
                pass
        
        # Return the highest confidence result
        if results:
            return max(results, key=lambda x: x[1])
        
        return None, 0
    
    def identify_router(self, host: str, open_ports: List[int]) -> Tuple[str, float]:
        """Identify if device is a router/gateway"""
        router_indicators = 0
        
        # Check if it has typical router ports
        if 53 in open_ports:  # DNS
            router_indicators += 1
        if any(p in open_ports for p in [80, 443]):  # Web interface
            router_indicators += 1
        if 22 in open_ports or 23 in open_ports:  # SSH/Telnet
            router_indicators += 1
        
        # Check if it's .1 address (common for gateways)
        if host.endswith('.1'):
            router_indicators += 2
        
        # Try to identify specific router types
        if router_indicators >= 2:
            # Check for UniFi
            try:
                # UniFi typically runs on 8443
                if 8443 in open_ports:
                    response = requests.get(f"https://{host}:8443", verify=False, timeout=2)
                    if 'unifi' in response.text.lower():
                        return 'unifi_gateway', 0.95
            except:
                pass
            
            # Check for pfSense
            try:
                if 443 in open_ports:
                    response = requests.get(f"https://{host}", verify=False, timeout=2)
                    if 'pfsense' in response.text.lower():
                        return 'pfsense', 0.95
            except:
                pass
            
            # Generic router
            if router_indicators >= 3:
                return 'router', 0.85
        
        return None, 0
    
    def is_docker_container(self, host: str, hostname: str) -> bool:
        """Check if host is likely a Docker container"""
        # Docker containers often have specific hostname patterns
        docker_patterns = [
            hostname.lower() == 'unknown',
            hostname.startswith('container'),
            len(hostname) == 12 and all(c in '0123456789abcdef' for c in hostname),  # Container ID
            '.docker' in hostname,
            '.local' not in hostname and '.' not in hostname,  # No domain
        ]
        
        # Check IP patterns (Docker default subnets)
        docker_subnets = ['172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.']
        if any(host.startswith(subnet) for subnet in docker_subnets):
            return True
        
        return any(docker_patterns)
    
    def identify_service_smart(self, host: str, port: int, open_ports: List[int], hostname: str) -> Tuple[str, float]:
        """Smart service identification with context"""
        # First check if it's a router
        router_type, confidence = self.identify_router(host, open_ports)
        if router_type and confidence > 0.8:
            # Don't identify DNS on routers as Pi-hole
            if port == 53:
                return None, 0
            # Don't identify web interface as generic web server
            if port in [80, 443]:
                return router_type, confidence
        
        # Check if it's a Docker container
        is_container = self.is_docker_container(host, hostname)
        
        # If it's a container, boost confidence for container services
        base_service, base_confidence = self.identify_service(host, port)
        
        if is_container and base_service:
            # Boost confidence for services commonly run in Docker
            docker_services = ['plex', 'jellyfin', 'radarr', 'sonarr', 'prowlarr', 
                              'portainer', 'nginx', 'traefik', 'grafana', 'influxdb']
            if any(svc in base_service.lower() for svc in docker_services):
                base_confidence = min(base_confidence * 1.2, 0.99)
        
        return base_service, base_confidence
    
    def _check_http_response(self, host: str, port: int) -> Tuple[str, float]:
        """Check HTTP/HTTPS response headers and content"""
        protocols = ['http', 'https'] if port == 443 else ['http']
        
        for protocol in protocols:
            try:
                url = f"{protocol}://{host}:{port}"
                response = requests.get(url, timeout=self.timeout, verify=False, allow_redirects=True)
                
                # Check headers
                headers = response.headers
                content = response.text.lower()
                
                # Service-specific identifications
                checks = [
                    # Plex
                    ('plex', 0.9, [
                        lambda: 'plex' in headers.get('X-Plex-Protocol', '').lower(),
                        lambda: 'x-plex-version' in headers,
                        lambda: 'plex media server' in content,
                    ]),
                    
                    # Jellyfin
                    ('jellyfin', 0.9, [
                        lambda: 'jellyfin' in headers.get('Server', '').lower(),
                        lambda: 'jellyfin' in content,
                        lambda: '/web/index.html' in content and 'jellyfin' in content,
                    ]),
                    
                    # Radarr
                    ('radarr', 0.95, [
                        lambda: 'radarr' in content,
                        lambda: '<title>radarr</title>' in content,
                        lambda: port == 7878,
                    ]),
                    
                    # Sonarr
                    ('sonarr', 0.95, [
                        lambda: 'sonarr' in content,
                        lambda: '<title>sonarr</title>' in content,
                        lambda: port == 8989,
                    ]),
                    
                    # Prowlarr
                    ('prowlarr', 0.95, [
                        lambda: 'prowlarr' in content,
                        lambda: '<title>prowlarr</title>' in content,
                        lambda: port == 9696,
                    ]),
                    
                    # Pi-hole
                    ('pihole', 0.95, [
                        lambda: 'pi-hole' in content,
                        lambda: '/admin/api.php' in content,
                        lambda: 'x-pi-hole' in headers,
                    ]),
                    
                    # Portainer
                    ('portainer', 0.95, [
                        lambda: 'portainer' in content,
                        lambda: port == 9000,
                    ]),
                    
                    # UniFi Controller
                    ('unifi', 0.9, [
                        lambda: 'unifi' in content,
                        lambda: port == 8443,
                    ]),
                ]
                
                # Check each service
                for service_name, base_confidence, checks_list in checks:
                    matches = sum(1 for check in checks_list if self._safe_check(check))
                    if matches > 0:
                        confidence = base_confidence * (matches / len(checks_list))
                        return service_name, confidence
                        
            except Exception as e:
                pass
        
        return None, 0
    
    def _check_banner(self, host: str, port: int) -> Tuple[str, float]:
        """Check service banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((host, port))
            
            # For some services, we need to send data first
            if port in [80, 8080, 8096, 32400]:
                sock.send(b"GET / HTTP/1.0\r\n\r\n")
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').lower()
            sock.close()
            
            # Check banner content
            banner_checks = [
                ('plex', 0.8, ['plex media server']),
                ('ssh', 0.95, ['ssh-', 'openssh']),
                ('ftp', 0.9, ['ftp', '220 ']),
            ]
            
            for service, confidence, keywords in banner_checks:
                if any(keyword in banner for keyword in keywords):
                    return service, confidence
                    
        except:
            pass
            
        return None, 0
    
    def _check_specific_endpoints(self, host: str, port: int) -> Tuple[str, float]:
        """Check specific API endpoints"""
        endpoint_checks = [
            # Plex
            ('plex', '/identity', lambda r: 'machineidentifier' in r.text.lower(), 32400),
            
            # Radarr
            ('radarr', '/api/v3/config/ui', lambda r: True, 7878),
            
            # Sonarr  
            ('sonarr', '/api/v3/config/ui', lambda r: True, 8989),
            
            # Prowlarr
            ('prowlarr', '/api/v1/config/ui', lambda r: True, 9696),
        ]
        
        for service, endpoint, check_func, expected_port in endpoint_checks:
            if port == expected_port:
                try:
                    url = f"http://{host}:{port}{endpoint}"
                    response = requests.get(url, timeout=self.timeout)
                    if response.status_code == 200 and check_func(response):
                        return service, 0.95
                except:
                    pass
        
        return None, 0
    
    def _safe_check(self, check_func):
        """Safely execute a check function"""
        try:
            return check_func()
        except:
            return False
    
    def identify_printer(self, host: str) -> bool:
        """Check if a device is a printer"""
        printer_ports = [631, 9100, 515]  # IPP, RAW, LPR
        
        for port in printer_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    return True
            except:
                pass
                
        return False
    
    def get_device_type(self, host: str, open_ports: List[int]) -> str:
        """Determine device type based on open ports"""
        # Check for printer
        if self.identify_printer(host):
            return "printer"
            
        # Router/Gateway signatures
        if all(p in open_ports for p in [53, 80]) and host.endswith('.1'):
            return "router"
            
        return "unknown"

    def identify_service_safe(self, host: str, port: int) -> Tuple[str, float]:
        """Safe wrapper for service identification"""
        try:
            return self.identify_service(host, port)
        except Exception as e:
            # Return none on any error
            return None, 0
