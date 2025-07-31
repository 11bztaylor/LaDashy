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
