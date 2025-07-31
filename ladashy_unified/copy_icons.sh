#!/bin/bash
# Copy icons from cloned repository

ICON_SOURCE="/tmp/selfhst-icons/png"
ICON_DEST="/home/zach/homelab-documentation/ladashy_unified/icons"

# Function to copy icon with both variants
copy_icon() {
    local source_name=$1
    local dest_name=$2
    
    # Copy light variant
    if [ -f "$ICON_SOURCE/${source_name}.png" ]; then
        cp "$ICON_SOURCE/${source_name}.png" "$ICON_DEST/${dest_name}_light.png"
        echo "✓ Copied ${source_name}.png → ${dest_name}_light.png"
    fi
    
    # Copy dark variant (some repos have -dark suffix)
    if [ -f "$ICON_SOURCE/${source_name}-dark.png" ]; then
        cp "$ICON_SOURCE/${source_name}-dark.png" "$ICON_DEST/${dest_name}_dark.png"
    elif [ -f "$ICON_SOURCE/${source_name}_dark.png" ]; then
        cp "$ICON_SOURCE/${source_name}_dark.png" "$ICON_DEST/${dest_name}_dark.png"
    else
        # If no dark variant, use light for both
        cp "$ICON_SOURCE/${source_name}.png" "$ICON_DEST/${dest_name}_dark.png" 2>/dev/null
    fi
}

# Copy all service icons
echo "Copying service icons..."

# Media Services
copy_icon "plex" "plex"
copy_icon "jellyfin" "jellyfin"
copy_icon "emby" "emby"
copy_icon "radarr" "radarr"
copy_icon "sonarr" "sonarr"
copy_icon "lidarr" "lidarr"
copy_icon "readarr" "readarr"
copy_icon "bazarr" "bazarr"
copy_icon "prowlarr" "prowlarr"
copy_icon "overseerr" "overseerr"
copy_icon "ombi" "ombi"
copy_icon "tautulli" "tautulli"

# Download Clients
copy_icon "qbittorrent" "qbittorrent"
copy_icon "transmission" "transmission"
copy_icon "sabnzbd" "sabnzbd"
copy_icon "nzbget" "nzbget"
copy_icon "deluge" "deluge"

# Network Services
copy_icon "nginx-proxy-manager" "nginx-proxy-manager"
copy_icon "traefik" "traefik"
copy_icon "caddy" "caddy"
copy_icon "pihole" "pihole"
copy_icon "adguard-home" "adguard-home"
copy_icon "wireguard" "wireguard"
copy_icon "openvpn" "openvpn"
copy_icon "tailscale" "tailscale"

# Monitoring
copy_icon "grafana" "grafana"
copy_icon "prometheus" "prometheus"
copy_icon "influxdb" "influxdb"
copy_icon "uptime-kuma" "uptime-kuma"
copy_icon "netdata" "netdata"
copy_icon "glances" "glances"

# Management
copy_icon "portainer" "portainer"
copy_icon "yacht" "yacht"
copy_icon "cockpit" "cockpit"
copy_icon "webmin" "webmin"

# Home Automation
copy_icon "home-assistant" "home-assistant"
copy_icon "node-red" "node-red"
copy_icon "mosquitto" "mosquitto"
copy_icon "zigbee2mqtt" "zigbee2mqtt"
copy_icon "esphome" "esphome"

# Storage
copy_icon "nextcloud" "nextcloud"
copy_icon "syncthing" "syncthing"
copy_icon "minio" "minio"
copy_icon "duplicati" "duplicati"
copy_icon "photoprism" "photoprism"
copy_icon "immich" "immich"

# Default/fallback
copy_icon "dashboard" "dashboard"

echo ""
echo "✅ Icon copy complete!"
echo ""
echo "Icons copied: $(ls -1 $ICON_DEST | wc -l)"
