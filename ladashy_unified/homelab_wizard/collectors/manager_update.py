# Add this to the existing manager.py file in the collectors dict:

from .jellyfin_collector import JellyfinCollector
from .portainer_collector import PortainerCollector  
from .pihole_collector import PiholeCollector

# Update the collectors dictionary:
collectors = {
    'plex': PlexCollector,
    'radarr': RadarrCollector,
    'sonarr': SonarrCollector,
    'jellyfin': JellyfinCollector,
    'portainer': PortainerCollector,
    'pihole': PiholeCollector,
    'pi-hole': PiholeCollector,
}
