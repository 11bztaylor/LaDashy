"""
Radarr data collector
"""
import requests
from typing import Dict, Any, Tuple
from .base_collector import BaseCollector

class RadarrCollector(BaseCollector):
    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.base_url = f"http://{config['host']}:{config.get('port', '7878')}"
        if config.get('base_url'):
            self.base_url += config['base_url']
        self.headers = {}
        if 'api_key' in config:
            self.headers['X-Api-Key'] = config['api_key']
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test Radarr connection"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v3/system/status",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                return True, "Connected to Radarr"
            elif response.status_code == 401:
                return False, "Authentication failed - check API key"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def collect_basic_info(self) -> Dict[str, Any]:
        """Collect basic Radarr information"""
        try:
            # System status
            status = requests.get(
                f"{self.base_url}/api/v3/system/status",
                headers=self.headers
            ).json()
            
            return {
                "version": status.get("version"),
                "build_time": status.get("buildTime"),
                "start_time": status.get("startTime"),
                "app_name": status.get("appName"),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def collect_detailed_info(self) -> Dict[str, Any]:
        """Collect detailed Radarr information"""
        try:
            detailed = {}
            
            # Movie statistics
            movies = requests.get(
                f"{self.base_url}/api/v3/movie",
                headers=self.headers
            ).json()
            
            detailed['total_movies'] = len(movies)
            detailed['monitored_movies'] = sum(1 for m in movies if m.get('monitored'))
            detailed['downloaded_movies'] = sum(1 for m in movies if m.get('hasFile'))
            
            # Root folders
            root_folders = requests.get(
                f"{self.base_url}/api/v3/rootfolder",
                headers=self.headers
            ).json()
            
            detailed['root_folders'] = [
                {
                    "path": rf.get("path"),
                    "free_space": rf.get("freeSpace"),
                    "total_space": rf.get("totalSpace")
                }
                for rf in root_folders
            ]
            
            # Queue info
            queue = requests.get(
                f"{self.base_url}/api/v3/queue",
                headers=self.headers
            ).json()
            
            detailed['queue_count'] = queue.get('totalRecords', 0)
            
            return detailed
        except Exception as e:
            return {"error": str(e)}
