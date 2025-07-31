"""
Documentation generator framework for LaDashy
Generates comprehensive homelab documentation in multiple formats
"""
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import markdown
from jinja2 import Environment, FileSystemLoader, Template

class DocumentationGenerator:
    def __init__(self, output_dir: str = "homelab_docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.dirs = {
            'services': self.output_dir / 'services',
            'network': self.output_dir / 'network',
            'docker': self.output_dir / 'docker',
            'configs': self.output_dir / 'configs',
            'diagrams': self.output_dir / 'diagrams',
            'assets': self.output_dir / 'assets'
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)
            
    def generate_all(self, 
                     discovered_services: Dict,
                     service_configs: Dict,
                     collected_data: Dict) -> Dict[str, str]:
        """Generate all documentation"""
        results = {}
        
        # Generate main index
        results['index'] = self._generate_index(discovered_services, service_configs)
        
        # Generate network topology
        results['network'] = self._generate_network_topology(discovered_services)
        
        # Generate service documentation
        for host, services in discovered_services.items():
            for service in services.get('services', []):
                service_key = f"{service['name']}_{host}"
                results[service_key] = self._generate_service_doc(
                    service, host, 
                    service_configs.get(service_key, {}),
                    collected_data.get(service_key, {})
                )
        
        # Generate Docker compose files
        results['docker'] = self._generate_docker_compose(discovered_services, service_configs)
        
        # Generate dependency map
        results['dependencies'] = self._generate_dependency_map(discovered_services)
        
        # Generate security audit
        results['security'] = self._generate_security_audit(discovered_services, service_configs)
        
        return results
    
    def _generate_index(self, discovered_services: Dict, service_configs: Dict) -> str:
        """Generate main index page"""
        template = """# Homelab Documentation

Generated: {{ timestamp }}

## Overview

This documentation provides a comprehensive view of your homelab infrastructure.

## Quick Stats

- **Total Hosts**: {{ total_hosts }}
- **Total Services**: {{ total_services }}
- **Configured Services**: {{ configured_services }}
- **Docker Containers**: {{ docker_containers }}

## Network Overview

| Host | IP Address | Services | Status |
|------|------------|----------|--------|
{% for host, info in discovered_services.items() %}
| {{ info.hostname }} | {{ host }} | {{ info.services|length }} services | ✅ Active |
{% endfor %}

## Services by Category

### Media Services
{% for host, info in discovered_services.items() %}
{% for service in info.services %}
{% if service.name in ['Plex', 'Jellyfin', 'Emby', 'Radarr', 'Sonarr', 'Prowlarr'] %}
- [{{ service.name }}](services/{{ service.name|lower|replace(' ', '_') }}_{{ host }}.md) on {{ info.hostname }} ({{ host }})
{% endif %}
{% endfor %}
{% endfor %}

### Network Services
{% for host, info in discovered_services.items() %}
{% for service in info.services %}
{% if service.name in ['Pi-hole', 'Nginx Proxy Manager', 'Traefik'] %}
- [{{ service.name }}](services/{{ service.name|lower|replace(' ', '_') }}_{{ host }}.md) on {{ info.hostname }} ({{ host }})
{% endif %}
{% endfor %}
{% endfor %}

### Management Tools
{% for host, info in discovered_services.items() %}
{% for service in info.services %}
{% if service.name in ['Portainer', 'Cockpit', 'Webmin'] %}
- [{{ service.name }}](services/{{ service.name|lower|replace(' ', '_') }}_{{ host }}.md) on {{ info.hostname }} ({{ host }})
{% endif %}
{% endfor %}
{% endfor %}

## Quick Links

- [Network Topology](network/topology.md)
- [Service Dependencies](network/dependencies.md)
- [Docker Compose Files](docker/README.md)
- [Security Audit](security_audit.md)
- [Backup Status](backup_status.md)
"""
        
        # Calculate stats
        total_services = sum(len(info.get('services', [])) for info in discovered_services.values())
        configured_services = len(service_configs)
        docker_containers = sum(
            1 for info in discovered_services.values() 
            for service in info.get('services', [])
            if service.get('container')
        )
        
        # Render template
        from jinja2 import Template
        tmpl = Template(template)
        content = tmpl.render(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            discovered_services=discovered_services,
            total_hosts=len(discovered_services),
            total_services=total_services,
            configured_services=configured_services,
            docker_containers=docker_containers
        )
        
        # Save to file
        output_path = self.output_dir / 'README.md'
        output_path.write_text(content)
        
        return content
    
    def _generate_service_doc(self, service: Dict, host: str, 
                             config: Dict, data: Dict) -> str:
        """Generate documentation for a single service"""
        template = """# {{ service.name }}

## Overview

- **Host**: {{ hostname }} ({{ host }})
- **Port(s)**: {{ ports }}
- **Confidence**: {{ confidence }}%
- **Type**: {{ service.get('device_type', 'Unknown') }}

## Configuration

{% if config %}
### Current Configuration
```yaml
{{ config | tojson(indent=2) }}
```
{% else %}
❌ **Not Configured** - Add configuration in LaDashy to enable monitoring
{% endif %}

## Connection Details

- **URL**: http://{{ host }}:{{ service.ports[0] if service.ports else 'N/A' }}
{% if config.get('api_key') %}
- **API Key**: ✅ Configured
{% endif %}
{% if config.get('username') %}
- **Username**: {{ config.username }}
{% endif %}

## Docker Compose Example

```yaml
version: '3.8'
services:
  {{ service.name|lower|replace(' ', '-') }}:
    image: # Add appropriate image
    container_name: {{ service.name|lower|replace(' ', '-') }}
    ports:
      - "{{ service.ports[0] if service.ports else 8080 }}:{{ service.ports[0] if service.ports else 8080 }}"
    volumes:
      - ./config:/config
      - ./data:/data
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    restart: unless-stopped
```

---
*Last Updated: {{ timestamp }}*
"""
        
        # Get hostname
        hostname = 'Unknown'
        
        # Render template
        from jinja2 import Template
        tmpl = Template(template)
        content = tmpl.render(
            service=service,
            host=host,
            hostname=hostname,
            ports=', '.join(str(p) for p in service.get('ports', [])),
            confidence=int(service.get('confidence', 0) * 100),
            config=config,
            data=data,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Save to file
        filename = f"{service['name'].lower().replace(' ', '_')}_{host}.md"
        output_path = self.dirs['services'] / filename
        output_path.write_text(content)
        
        return content
    
    def _generate_network_topology(self, discovered_services: Dict) -> str:
        """Generate network topology diagram and documentation"""
        
        # Create Mermaid diagram
        mermaid_diagram = """graph TB
    subgraph Internet
        WAN[Internet]
    end
    
    subgraph "Home Network"
        Router[Router<br/>192.168.1.1]
        WAN --> Router
"""
        
        # Add discovered hosts
        for host, info in discovered_services.items():
            host_id = host.replace('.', '_')
            services_list = '<br/>'.join(s['name'] for s in info.get('services', [])[:3])
            if len(info.get('services', [])) > 3:
                services_list += '<br/>...'
            
            mermaid_diagram += f"""
        {host_id}[{info['hostname']}<br/>{host}<br/>{services_list}]
        Router --> {host_id}"""
        
        mermaid_diagram += "\n    end"
        
        # Create markdown document
        content = f"""# Network Topology

## Network Diagram

```mermaid
{mermaid_diagram}
```

## Host Details

| Hostname | IP Address | Services | Open Ports |
|----------|------------|----------|------------|
"""
        
        for host, info in discovered_services.items():
            services = ', '.join(s['name'] for s in info.get('services', []))
            ports = ', '.join(str(p) for s in info.get('services', []) for p in s.get('ports', []))
            
            content += f"| {info['hostname']} | {host} | {services} | {ports} |\n"
        
        content += """

---
*Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
        
        # Save to file
        output_path = self.dirs['network'] / 'topology.md'
        output_path.write_text(content)
        
        # Also create an HTML version with interactive diagram
        html_content = self._generate_html_network_diagram(discovered_services)
        html_path = self.dirs['diagrams'] / 'network_topology.html'
        html_path.write_text(html_content)
        
        return content
    
    def _generate_html_network_diagram(self, discovered_services: Dict) -> str:
        """Generate interactive HTML network diagram"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Homelab Network Topology</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        #network { width: 100%; height: 600px; border: 1px solid #ccc; }
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .info { margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Homelab Network Topology</h1>
    <div class="info">
        <strong>Interactive Network Diagram</strong><br>
        Click and drag to move nodes. Scroll to zoom. Click on a node for details.
    </div>
    <div id="network"></div>
    <script>
        // Create nodes
        var nodes = new vis.DataSet([
            {id: 'internet', label: 'Internet', shape: 'square', color: '#ff6b6b', size: 30},
            {id: 'router', label: 'Router\\n192.168.1.1', shape: 'box', color: '#4ecdc4', size: 25},
""" + '\n'.join([f"""            {{id: '{host.replace(".", "_")}', label: '{info["hostname"]}\\n{host}\\n{len(info.get("services", []))} services', shape: 'box', color: '#45b7d1'}},""" 
                for host, info in discovered_services.items()]) + """
        ]);
        
        // Create edges
        var edges = new vis.DataSet([
            {from: 'internet', to: 'router', width: 3},
""" + '\n'.join([f"""            {{from: 'router', to: '{host.replace(".", "_")}'}},""" 
                for host in discovered_services.keys()]) + """
        ]);
        
        // Create network
        var container = document.getElementById('network');
        var data = { nodes: nodes, edges: edges };
        var options = {
            physics: {
                enabled: true,
                barnesHut: {
                    springConstant: 0.04,
                    avoidOverlap: 0.5
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200
            }
        };
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>"""
    
    def _generate_dependency_map(self, discovered_services: Dict) -> str:
        """Generate service dependency map"""
        content = """# Service Dependencies

## Dependency Graph

```mermaid
graph LR
    subgraph "Media Stack"
        Plex[Plex Media Server]
        Radarr[Radarr]
        Sonarr[Sonarr]
        Prowlarr[Prowlarr]
        
        Prowlarr -->|Indexers| Radarr
        Prowlarr -->|Indexers| Sonarr
        Radarr -->|Movies| Plex
        Sonarr -->|TV Shows| Plex
    end
    
    subgraph "Download Stack"
        qBittorrent[qBittorrent]
        Radarr -->|Downloads| qBittorrent
        Sonarr -->|Downloads| qBittorrent
    end
    
    subgraph "Network Services"
        NPM[Nginx Proxy Manager]
        NPM -->|Reverse Proxy| Plex
        NPM -->|Reverse Proxy| Radarr
        NPM -->|Reverse Proxy| Sonarr
    end
```

---
*Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
        
        # Save to file
        output_path = self.dirs['network'] / 'dependencies.md'
        output_path.write_text(content)
        
        return content
    
    def _generate_docker_compose(self, discovered_services: Dict, service_configs: Dict) -> str:
        """Generate Docker compose configurations"""
        
        # Main compose file
        compose_content = """version: '3.8'

networks:
  homelab:
    driver: bridge

services:
"""
        
        # Add each discovered service
        service_num = 10
        for host, info in discovered_services.items():
            for service in info.get('services', []):
                if service.get('container'):
                    service_name = service['name'].lower().replace(' ', '-')
                    compose_content += f"""
  {service_name}:
    image: # TODO: Add image for {service['name']}
    container_name: {service_name}
    ports:
      - "{service['ports'][0] if service.get('ports') else 8080}:{service['ports'][0] if service.get('ports') else 8080}"
    volumes:
      - ./config/{service_name}:/config
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    restart: unless-stopped
"""
                    service_num += 1
        
        # Save main compose file
        compose_path = self.dirs['docker'] / 'docker-compose.yml'
        compose_path.write_text(compose_content)
        
        # Create README for docker directory
        docker_readme = """# Docker Compose Files

This directory contains Docker Compose configurations for your homelab services.

## Usage

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f service-name
```
"""
        
        readme_path = self.dirs['docker'] / 'README.md'
        readme_path.write_text(docker_readme)
        
        return compose_content
    
    def _generate_security_audit(self, discovered_services: Dict, service_configs: Dict) -> str:
        """Generate security audit report"""
        content = f"""# Security Audit Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This security audit provides an overview of your homelab's security posture.

## Exposed Services

### Externally Accessible Services

| Service | Host | Port | Protection |
|---------|------|------|------------|
"""
        
        # Check for services on common web ports
        for host, info in discovered_services.items():
            for service in info.get('services', []):
                for port in service.get('ports', []):
                    if port in [80, 443, 8080, 8443]:
                        protection = "⚠️ Check reverse proxy" if port in [80, 8080] else "✅ HTTPS"
                        content += f"| {service['name']} | {host} | {port} | {protection} |\n"
        
        content += """

## Security Checklist

### Access Control
- [ ] All services behind reverse proxy with authentication
- [ ] Strong passwords on all services (min 16 characters)
- [ ] 2FA enabled where available
- [ ] API keys rotated regularly
- [ ] Default credentials changed

### Network Security
- [ ] Firewall enabled and configured
- [ ] Only necessary ports exposed
- [ ] VLANs configured for network segmentation
- [ ] VPN for remote access (not port forwarding)
- [ ] Regular security updates applied

---
*This is an automated security audit. For comprehensive security assessment, consider professional penetration testing.*
"""
        
        # Save to file
        output_path = self.output_dir / 'security_audit.md'
        output_path.write_text(content)
        
        return content
    
    def export_to_json(self, discovered_services: Dict, service_configs: Dict, 
                      collected_data: Dict) -> str:
        """Export all data to JSON for AI assistant consumption"""
        export_data = {
            'generated': datetime.now().isoformat(),
            'summary': {
                'total_hosts': len(discovered_services),
                'total_services': sum(len(info.get('services', [])) for info in discovered_services.values()),
                'configured_services': len(service_configs)
            },
            'discovered_services': discovered_services,
            'service_configurations': service_configs,
            'collected_data': collected_data
        }
        
        # Save to file
        json_path = self.output_dir / 'homelab_data.json'
        with open(json_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return json.dumps(export_data, indent=2)
    
    def export_to_html_dashboard(self, discovered_services: Dict, 
                                service_configs: Dict) -> str:
        """Generate an HTML dashboard"""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homelab Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a1a;
            color: #e0e0e0;
        }
        .header {
            background: #2d2d2d;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .header h1 {
            margin: 0;
            color: #4ecdc4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            color: #96ceb4;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #4ecdc4;
        }
        .services {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .service-card {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        .service-card:hover {
            transform: translateY(-5px);
        }
        .service-card h4 {
            margin: 0 0 10px 0;
            color: #4ecdc4;
        }
        .service-info {
            font-size: 0.9em;
            color: #b0b0b0;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-active { background: #96ceb4; }
        .status-configured { background: #ffd93d; }
        .status-error { background: #ff6b6b; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🏠 Homelab Dashboard</h1>
            <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>Total Hosts</h3>
                <div class="value">""" + str(len(discovered_services)) + """</div>
            </div>
            <div class="stat-card">
                <h3>Total Services</h3>
                <div class="value">""" + str(sum(len(info.get('services', [])) for info in discovered_services.values())) + """</div>
            </div>
            <div class="stat-card">
                <h3>Configured</h3>
                <div class="value">""" + str(len(service_configs)) + """</div>
            </div>
        </div>
        
        <h2>Services</h2>
        <div class="services">
"""
        
        # Add service cards
        for host, info in discovered_services.items():
            for service in info.get('services', []):
                service_key = f"{service['name']}_{host}"
                is_configured = service_key in service_configs
                
                html_content += f"""
            <div class="service-card">
                <h4>
                    <span class="status-indicator status-{'configured' if is_configured else 'active'}"></span>
                    {service['name']}
                </h4>
                <div class="service-info">
                    <p><strong>Host:</strong> {info['hostname']} ({host})</p>
                    <p><strong>Port:</strong> {', '.join(str(p) for p in service.get('ports', []))}</p>
                    <p><strong>Status:</strong> {'Configured' if is_configured else 'Discovered'}</p>
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>"""
        
        # Save to file
        dashboard_path = self.output_dir / 'dashboard.html'
        dashboard_path.write_text(html_content)
        
        return html_content


# Integration function for LaDashy
def generate_documentation(discovered_services: Dict, 
                         service_configs: Dict,
                         collected_data: Dict,
                         output_dir: str = "homelab_docs") -> Dict[str, str]:
    """
    Main entry point for documentation generation
    
    Args:
        discovered_services: Services discovered by scanner
        service_configs: Configuration for each service
        collected_data: Live data collected from services
        output_dir: Output directory for documentation
    
    Returns:
        Dictionary of generated file paths
    """
    generator = DocumentationGenerator(output_dir)
    
    # Generate all documentation
    results = generator.generate_all(discovered_services, service_configs, collected_data)
    
    # Export to different formats
    generator.export_to_json(discovered_services, service_configs, collected_data)
    generator.export_to_html_dashboard(discovered_services, service_configs)
    
    return results
