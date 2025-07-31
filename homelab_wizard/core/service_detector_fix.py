# Add these methods to the ServiceDetector class

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
        hostname == 'unknown',
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
