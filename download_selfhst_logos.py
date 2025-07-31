#!/usr/bin/env python3
"""
Download service logos from selfhst/icons repository
"""
import os
import requests
import sys
from PIL import Image
import io

# Logo directory
LOGO_DIR = "homelab_wizard/assets/logos"
os.makedirs(LOGO_DIR, exist_ok=True)

# Base URL for selfhst icons
BASE_URL = "https://raw.githubusercontent.com/selfhst/icons/main/png"

# Mapping of our service names to selfhst icon names
SERVICE_ICON_MAP = {
    # Media Servers
    "Plex": "plex",
    "Jellyfin": "jellyfin",
    "Emby": "emby",
    "Kodi": "kodi",
    
    # Media Management
    "Radarr": "radarr",
    "Sonarr": "sonarr",
    "Lidarr": "lidarr",
    "Readarr": "readarr",
    "Bazarr": "bazarr",
    "Prowlarr": "prowlarr",
    "Overseerr": "overseerr",
    "Ombi": "ombi",
    "Tautulli": "tautulli",
    
    # Download Clients
    "qBittorrent": "qbittorrent",
    "Transmission": "transmission",
    "SABnzbd": "sabnzbd",
    "NZBGet": "nzbget",
    "Deluge": "deluge",
    
    # Network Services
    "Nginx Proxy Manager": "nginx-proxy-manager",
    "Traefik": "traefik",
    "Caddy": "caddy",
    "Pi-hole": "pi-hole",
    "AdGuard Home": "adguard-home",
    "WireGuard": "wireguard",
    "OpenVPN": "openvpn",
    "Tailscale": "tailscale",
    
    # Monitoring
    "Grafana": "grafana",
    "Prometheus": "prometheus",
    "InfluxDB": "influxdb",
    "Uptime Kuma": "uptime-kuma",
    "Netdata": "netdata",
    "Glances": "glances",
    
    # Management
    "Portainer": "portainer",
    "Yacht": "yacht",
    "Cockpit": "cockpit",
    "Webmin": "webmin",
    
    # Home Automation
    "Home Assistant": "home-assistant",
    "Node-RED": "node-red",
    "Mosquitto": "mqtt",
    "Zigbee2MQTT": "zigbee2mqtt",
    "ESPHome": "esphome",
    
    # Storage & Backup
    "Nextcloud": "nextcloud",
    "Syncthing": "syncthing",
    "MinIO": "minio",
    "Duplicati": "duplicati",
    "PhotoPrism": "photoprism",
    "Immich": "immich",
    
    # Security
    "Vaultwarden": "vaultwarden",
    "Authelia": "authelia",
    "Authentik": "authentik",
    "Keycloak": "keycloak",
    
    # Dashboards
    "Homepage": "homepage",
    "Heimdall": "heimdall",
    "Organizr": "organizr",
    "Dashy": "dashy",
    "Homarr": "homarr",
    "Flame": "flame",
    
    # Development
    "GitLab": "gitlab",
    "Gitea": "gitea",
    "Code Server": "code-server",
    "Jenkins": "jenkins",
    "Drone": "drone-ci",
    
    # Other Services
    "Docker": "docker",
    "PostgreSQL": "postgres",
    "MySQL/MariaDB": "mariadb",
    "Redis": "redis",
    "MongoDB": "mongodb",
}

def download_logo(service_name, icon_name):
    """Download a single logo"""
    url = f"{BASE_URL}/{icon_name}.png"
    
    try:
        print(f"Downloading {service_name} icon from {icon_name}.png...", end="")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Load the image
            img = Image.open(io.BytesIO(response.content))
            
            # Convert RGBA to RGB if necessary (for better compatibility)
            if img.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
            
            # Resize to standard sizes
            # Save original for high DPI displays
            img.save(os.path.join(LOGO_DIR, f"{icon_name}.png"))
            
            # Save smaller version for UI
            img_small = img.resize((32, 32), Image.Resampling.LANCZOS)
            img_small.save(os.path.join(LOGO_DIR, f"{icon_name}_32.png"))
            
            print(" ✓")
            return True
        else:
            print(f" ✗ (404)")
            return False
            
    except Exception as e:
        print(f" ✗ ({str(e)})")
        return False

def create_default_logo():
    """Create a default logo for services without icons"""
    img = Image.new('RGB', (32, 32), color='#666666')
    img.save(os.path.join(LOGO_DIR, "default.png"))
    img.save(os.path.join(LOGO_DIR, "default_32.png"))
    print("Created default logo ✓")

def main():
    print(f"Downloading logos to {LOGO_DIR}/")
    print("=" * 50)
    
    # Create default logo first
    create_default_logo()
    
    # Download all logos
    success_count = 0
    for service_name, icon_name in SERVICE_ICON_MAP.items():
        if download_logo(service_name, icon_name):
            success_count += 1
    
    print("=" * 50)
    print(f"Downloaded {success_count}/{len(SERVICE_ICON_MAP)} logos successfully")
    
    # Create simple name mappings for easy access
    print("\nCreating service name mappings...")
    for service_name, icon_name in SERVICE_ICON_MAP.items():
        # Create symlinks or copies with sanitized service names
        safe_name = service_name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        source = os.path.join(LOGO_DIR, f"{icon_name}_32.png")
        dest = os.path.join(LOGO_DIR, f"{safe_name}.png")
        
        if os.path.exists(source) and not os.path.exists(dest):
            try:
                if sys.platform != "win32":
                    os.symlink(source, dest)
                else:
                    # Copy on Windows
                    import shutil
                    shutil.copy2(source, dest)
            except:
                pass

if __name__ == "__main__":
    main()
