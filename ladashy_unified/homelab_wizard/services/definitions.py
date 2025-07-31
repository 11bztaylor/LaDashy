"""
Service definitions for homelab services
"""

# Service categories and their services
SERVICES = {
    "Media Servers": [
        {
            "name": "Plex",
            "icon": "plex",
            "containers": ["plex", "plexmediaserver"],
            "ports": [32400],
            "description": "Media server for streaming content"
        },
        {
            "name": "Jellyfin",
            "icon": "jellyfin",
            "containers": ["jellyfin"],
            "ports": [8096],
            "description": "Free and open source media server"
        },
        {
            "name": "Emby",
            "icon": "emby",
            "containers": ["emby", "embyserver"],
            "ports": [8096],
            "description": "Media server alternative"
        },
    ],
    
    "Media Management": [
        {
            "name": "Radarr",
            "icon": "radarr",
            "containers": ["radarr"],
            "ports": [7878],
            "description": "Movie collection manager"
        },
        {
            "name": "Sonarr",
            "icon": "sonarr",
            "containers": ["sonarr"],
            "ports": [8989],
            "description": "TV show collection manager"
        },
        {
            "name": "Prowlarr",
            "icon": "prowlarr",
            "containers": ["prowlarr"],
            "ports": [9696],
            "description": "Indexer manager for the *arr suite"
        },
    ],
    
    "Network Services": [
        {
            "name": "Nginx Proxy Manager",
            "icon": "nginx",
            "containers": ["nginx-proxy-manager", "nginxproxymanager"],
            "ports": [81],
            "description": "Easy reverse proxy with GUI"
        },
        {
            "name": "Pi-hole",
            "icon": "pihole",
            "containers": ["pihole"],
            "ports": [80, 53],
            "description": "Network-wide ad blocker"
        },
    ],
    
    "Management": [
        {
            "name": "Portainer",
            "icon": "portainer",
            "containers": ["portainer"],
            "ports": [9000],
            "description": "Docker management GUI"
        },
    ],
}

def get_all_services():
    """Get flat list of all services"""
    all_services = []
    for category, services in SERVICES.items():
        all_services.extend(services)
    return all_services

def get_service_by_name(name):
    """Get service info by name"""
    for service in get_all_services():
        if service["name"] == name:
            return service
    return None

# Add these additional services to the SERVICES dictionary
ADDITIONAL_SERVICES = {
    "Download Clients": [
        {
            "name": "qBittorrent",
            "icon": "default",
            "containers": ["qbittorrent", "binhex-qbittorrentvpn"],
            "ports": [8080, 6881, 8999],  # Added alternate ports
            "description": "BitTorrent client"
        },
        {
            "name": "Transmission",
            "icon": "default", 
            "containers": ["transmission"],
            "ports": [9091, 51413],
            "description": "BitTorrent client"
        },
        {
            "name": "Deluge",
            "icon": "default",
            "containers": ["deluge"],
            "ports": [8112, 58846],
            "description": "BitTorrent client"
        },
    ],
    "Monitoring": [
        {
            "name": "Prometheus",
            "icon": "prometheus",
            "containers": ["prometheus"],
            "ports": [9090],
            "description": "Metrics collection"
        },
        {
            "name": "InfluxDB",
            "icon": "default",
            "containers": ["influxdb"],
            "ports": [8086],
            "description": "Time series database"
        },
        {
            "name": "Uptime Kuma",
            "icon": "uptime_kuma",
            "containers": ["uptime-kuma"],
            "ports": [3001],
            "description": "Uptime monitoring"
        },
    ]
}

# Merge with existing services
for category, services in ADDITIONAL_SERVICES.items():
    if category in SERVICES:
        SERVICES[category].extend(services)
    else:
        SERVICES[category] = services

# Make sure all media services have the right ports
MEDIA_SERVICES_UPDATE = {
    "Radarr": [7878],
    "Sonarr": [8989],
    "Prowlarr": [9696],
    "Bazarr": [6767],
    "Lidarr": [8686],
    "Readarr": [8787],
    "Overseerr": [5055],
    "Ombi": [3579],
    "Tautulli": [8181],
}

# Update the services if they exist
for service_name, ports in MEDIA_SERVICES_UPDATE.items():
    for category in SERVICES.values():
        for service in category:
            if service["name"] == service_name:
                service["ports"] = ports
                break
