# Add this to the scanner.py file

    def scan_host_services_advanced(self, host: str, progress_callback=None) -> List[Dict]:
        """Advanced service detection with confidence scoring"""
        from ..services.definitions import get_all_services
        from .service_detector import ServiceDetector
        
        detector = ServiceDetector()
        discovered_services = []
        all_services = get_all_services()
        
        # First, get all open ports (quick scan of common ports)
        common_ports = [
            20, 21, 22, 23, 25, 53, 80, 81, 110, 111, 135, 139, 143, 443, 445,
            631, 993, 995, 1433, 1521, 3306, 3389, 5000, 5001, 5432, 5900, 6379,
            7878, 8080, 8081, 8096, 8123, 8181, 8443, 8989, 9000, 9090, 9100,
            27017, 32400
        ]
        
        if progress_callback:
            progress_callback(f"Scanning ports on {host}")
        
        open_ports = []
        for port in common_ports:
            if self._is_port_open(host, port):
                open_ports.append(port)
        
        # Check device type
        device_type = detector.get_device_type(host, open_ports)
        
        if device_type == "printer":
            if progress_callback:
                progress_callback(f"{host} identified as printer, skipping")
            return []
        
        # Now identify services on open ports
        service_matches = {}
        
        for port in open_ports:
            if progress_callback:
                progress_callback(f"Identifying service on {host}:{port}")
            
            service_name, confidence = detector.identify_service(host, port)
            
            if service_name and confidence > 0.5:  # Minimum confidence threshold
                if service_name not in service_matches or confidence > service_matches[service_name]['confidence']:
                    service_matches[service_name] = {
                        'port': port,
                        'confidence': confidence
                    }
        
        # Build final service list
        for service_name, match_info in service_matches.items():
            # Find service definition
            service_def = None
            for service in all_services:
                if service['name'].lower().replace(' ', '_') == service_name:
                    service_def = service
                    break
            
            if service_def:
                discovered_services.append({
                    "name": service_def["name"],
                    "host": host,
                    "ports": [match_info['port']],
                    "description": service_def["description"],
                    "confidence": match_info['confidence'],
                    "device_type": device_type
                })
        
        return discovered_services
    
    def _is_port_open(self, host: str, port: int) -> bool:
        """Quick check if port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
