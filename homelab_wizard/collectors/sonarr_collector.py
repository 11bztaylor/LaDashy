"""
Sonarr data collector
"""
import requests
from typing import Dict, Any, Tuple
from .base_collector import BaseCollector

class SonarrCollector(BaseCollector):
    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.base_url = f"http://{config['host']}:{config.get('port', '8989')}"
        if config.get('base_url'):
            self.base_url += config['base_url']
        self.headers = {}
        if 'api_key' in config:
            self.headers['X-Api-Key'] = config['api_key']
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test Sonarr connection"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v3/system/status",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                return True, "Connected to Sonarr"
            elif response.status_code == 401:
                return False, "Authentication failed - check API key"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def collect_basic_info(self) -> Dict[str, Any]:
        """Collect basic Sonarr information"""
        try:
            status = requests.get(
                f"{self.base_url}/api/v3/system/status",
                headers=self.headers
            ).json()
            
            return {
                "version": status.get("version"),
                "build_time": status.get("buildTime"),
                "app_name": status.get("appName", "Sonarr"),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def collect_detailed_info(self) -> Dict[str, Any]:
        """Collect detailed Sonarr information"""
        try:
            detailed = {}
            
            # Series statistics
            series = requests.get(
                f"{self.base_url}/api/v3/series",
                headers=self.headers
            ).json()
            
            detailed['total_series'] = len(series)
            detailed['monitored_series'] = sum(1 for s in series if s.get('monitored'))
            
            # Episode statistics
            total_episodes = 0
            downloaded_episodes = 0
            
            for show in series:
                stats = show.get('statistics', {})
                total_episodes += stats.get('totalEpisodeCount', 0)
                downloaded_episodes += stats.get('episodeFileCount', 0)
                
            detailed['total_episodes'] = total_episodes
            detailed['downloaded_episodes'] = downloaded_episodes
            
            # Queue info
            queue = requests.get(
                f"{self.base_url}/api/v3/queue",
                headers=self.headers
            ).json()
            
            detailed['queue_count'] = queue.get('totalRecords', 0)
            
            # Root folders
            root_folders = requests.get(
                f"{self.base_url}/api/v3/rootfolder",
                headers=self.headers
            ).json()
            
            detailed['root_folders'] = [
                {
                    "path": rf.get("path"),
                    "freeSpace": rf.get("freeSpace"),
                    "totalSpace": rf.get("totalSpace")
                }
                for rf in root_folders
            ]
            
            return detailed
        except Exception as e:
            return {"error": str(e)}
