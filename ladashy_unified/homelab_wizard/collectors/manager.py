"""
Data collection manager
"""
from typing import Dict, Any, Optional, Tuple
from .plex_collector import PlexCollector
from .radarr_collector import RadarrCollector
from .sonarr_collector import SonarrCollector
from .jellyfin_collector import JellyfinCollector
from .portainer_collector import PortainerCollector
from .pihole_collector import PiholeCollector
from .base_collector import BaseCollector

class CollectorManager:
    def __init__(self):
        self.collectors = {
            "Plex": PlexCollector,
            "Radarr": RadarrCollector,
            "Sonarr": SonarrCollector,
            "Jellyfin": JellyfinCollector,
            "Portainer": PortainerCollector,
            "Pi-hole": PiholeCollector,
        }
        
    def get_collector(self, service_name: str, config: Dict[str, str]) -> Optional[BaseCollector]:
        """Get appropriate collector for a service"""
        # Try exact match first
        collector_class = self.collectors.get(service_name)
        
        # If not found, try case-insensitive match
        if not collector_class:
            for key, value in self.collectors.items():
                if key.lower() == service_name.lower():
                    collector_class = value
                    break
        
        if collector_class:
            return collector_class(config)
        return None
        
    def test_service(self, service_name: str, config: Dict[str, str]) -> Tuple[bool, str]:
        """Test connection to a service"""
        collector = self.get_collector(service_name, config)
        if collector:
            return collector.test_connection()
        else:
            # Fallback to generic test
            from ..core.connection_tester import ConnectionTester
            tester = ConnectionTester()
            return tester.test_connection(service_name, config)
            
    def collect_service_data(self, service_name: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Collect all data from a service"""
        collector = self.get_collector(service_name, config)
        if collector:
            return collector.collect_all()
        else:
            return {
                "status": "error",
                "error": f"No collector available for {service_name}"
            }
