// Service icon mappings - using actual PNG icons
const SERVICE_ICON_MAP = {
    // Media Services
    'plex': 'plex',
    'jellyfin': 'jellyfin',
    'emby': 'emby',
    'kodi': 'kodi',
    'radarr': 'radarr',
    'sonarr': 'sonarr',
    'lidarr': 'lidarr',
    'readarr': 'readarr',
    'bazarr': 'bazarr',
    'prowlarr': 'prowlarr',
    'overseerr': 'overseerr',
    'ombi': 'ombi',
    'tautulli': 'tautulli',
    
    // Download Clients
    'qbittorrent': 'qbittorrent',
    'transmission': 'transmission',
    'sabnzbd': 'sabnzbd',
    'nzbget': 'nzbget',
    'deluge': 'deluge',
    
    // Network Services
    'nginx proxy manager': 'nginx-proxy-manager',
    'traefik': 'traefik',
    'caddy': 'caddy',
    'pi-hole': 'pihole',
    'adguard home': 'adguard-home',
    'wireguard': 'wireguard',
    'openvpn': 'openvpn',
    'tailscale': 'tailscale',
    
    // Monitoring
    'grafana': 'grafana',
    'prometheus': 'prometheus',
    'influxdb': 'influxdb',
    'uptime kuma': 'uptime-kuma',
    'netdata': 'netdata',
    'glances': 'glances',
    
    // Management
    'portainer': 'portainer',
    'yacht': 'yacht',
    'cockpit': 'cockpit',
    'webmin': 'webmin',
    
    // Home Automation
    'home assistant': 'home-assistant',
    'node-red': 'node-red',
    'mosquitto': 'mosquitto',
    'zigbee2mqtt': 'zigbee2mqtt',
    'esphome': 'esphome',
    
    // Storage & Backup
    'nextcloud': 'nextcloud',
    'syncthing': 'syncthing',
    'minio': 'minio',
    'duplicati': 'duplicati',
    'photoprism': 'photoprism',
    'immich': 'immich',
    
    // Default
    'default': 'dashboard'
};

// Theme detection
function getCurrentTheme() {
    // You can implement actual theme detection here
    // For now, let's use a CSS variable or localStorage
    return localStorage.getItem('theme') || 'dark';
}

function getServiceIcon(serviceName) {
    const normalized = serviceName.toLowerCase();
    const iconName = SERVICE_ICON_MAP[normalized] || SERVICE_ICON_MAP['default'];
    const theme = getCurrentTheme();
    
    // Return an img element instead of emoji
    const iconPath = `/icons/${iconName}_${theme}.png`;
    return `<img src="${iconPath}" alt="${serviceName}" class="service-icon-img" onerror="this.onerror=null; this.src='/icons/dashboard_${theme}.png';">`;
}

// For backward compatibility with emoji version
function getServiceIconEmoji(serviceName) {
    const SERVICE_EMOJI = {
        'plex': '🎬',
        'jellyfin': '🎭',
        'default': '🔧'
    };
    const normalized = serviceName.toLowerCase();
    return SERVICE_EMOJI[normalized] || SERVICE_EMOJI['default'];
}
