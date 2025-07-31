# Add this at the end of scanner.py

    def discover_all_services(self, progress_callback=None) -> Dict[str, List[Dict]]:
        """Discover all services on all networks"""
        all_services = {}
        
        # First, find all hosts
        hosts = self.scan_networks(progress_callback)
        
        # Import detector here to avoid circular imports
        try:
            from .service_detector import ServiceDetector
            detector = ServiceDetector()
            use_smart_detection = True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Warning: Smart detection unavailable: {e}")
            use_smart_detection = False
        
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
            
            # Use smart detection if available
            if use_smart_detection:
                # Check if it's a router first
                router_type, router_conf = detector.identify_router(ip, open_ports)
                if router_type and router_conf > 0.8:
                    # It's a router
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
            
            # Identify services on each port
            services = self.scan_host_services(ip, progress_callback)
            
            if services:
                all_services[ip] = {
                    "hostname": hostname,
                    "services": services
                }
        
        return all_services
