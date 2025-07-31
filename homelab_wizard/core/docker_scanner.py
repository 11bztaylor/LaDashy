"""
Docker-aware network scanner
"""
import docker
import requests
from typing import Dict, List, Optional

class DockerScanner:
    def __init__(self):
        self.docker_clients = {}
        
    def connect_to_docker_host(self, host: str, port: int = 2375) -> bool:
        """Connect to Docker daemon on remote host"""
        try:
            # Try to connect to Docker
            client = docker.DockerClient(base_url=f"tcp://{host}:{port}")
            client.ping()
            self.docker_clients[host] = client
            return True
        except:
            return False
    
    def get_docker_containers(self, host: str) -> List[Dict]:
        """Get list of containers from Docker host"""
        if host not in self.docker_clients:
            return []
        
        try:
            client = self.docker_clients[host]
            containers = client.containers.list(all=True)
            
            container_info = []
            for container in containers:
                # Get container details
                info = {
                    'name': container.name,
                    'id': container.short_id,
                    'image': container.image.tags[0] if container.image.tags else 'unknown',
                    'status': container.status,
                    'ports': container.ports,
                    'networks': list(container.attrs['NetworkSettings']['Networks'].keys()),
                    'ip_address': None
                }
                
                # Get IP address
                for network, config in container.attrs['NetworkSettings']['Networks'].items():
                    if config.get('IPAddress'):
                        info['ip_address'] = config['IPAddress']
                        break
                
                container_info.append(info)
            
            return container_info
        except Exception as e:
            return []
    
    def identify_container_services(self, containers: List[Dict]) -> Dict[str, str]:
        """Map container IPs to service names"""
        ip_to_service = {}
        
        for container in containers:
            if not container.get('ip_address'):
                continue
            
            # Identify service based on image name
            image = container.get('image', '').lower()
            service_mappings = {
                'plex': 'Plex',
                'jellyfin': 'Jellyfin',
                'radarr': 'Radarr',
                'sonarr': 'Sonarr',
                'prowlarr': 'Prowlarr',
                'bazarr': 'Bazarr',
                'lidarr': 'Lidarr',
                'overseerr': 'Overseerr',
                'tautulli': 'Tautulli',
                'portainer': 'Portainer',
                'nginx-proxy': 'Nginx Proxy Manager',
                'traefik': 'Traefik',
                'pihole': 'Pi-hole',
                'grafana': 'Grafana',
                'prometheus': 'Prometheus',
                'influxdb': 'InfluxDB',
                'homeassistant': 'Home Assistant',
                'mosquitto': 'Mosquitto',
                'mariadb': 'MariaDB',
                'postgres': 'PostgreSQL',
                'redis': 'Redis',
                'mongo': 'MongoDB',
            }
            
            for key, service_name in service_mappings.items():
                if key in image:
                    ip_to_service[container['ip_address']] = {
                        'service': service_name,
                        'container': container['name'],
                        'image': container['image']
                    }
                    break
        
        return ip_to_service
