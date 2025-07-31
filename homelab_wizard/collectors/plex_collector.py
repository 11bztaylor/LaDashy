"""
Plex data collector
"""
import requests
from typing import Dict, Any, Tuple
from .base_collector import BaseCollector

class PlexCollector(BaseCollector):
    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.base_url = f"http://{config['host']}:{config.get('port', '32400')}"
        self.headers = {}
        if 'token' in config:
            self.headers['X-Plex-Token'] = config['token']
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test Plex connection"""
        try:
            response = requests.get(
                f"{self.base_url}/identity",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                return True, "Connected to Plex"
            elif response.status_code == 401:
                return False, "Authentication failed - check token"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def collect_basic_info(self) -> Dict[str, Any]:
        """Collect basic Plex information"""
        try:
            # Server identity
            identity = requests.get(
                f"{self.base_url}/identity",
                headers=self.headers
            ).json()
            
            # Server preferences
            prefs = requests.get(
                f"{self.base_url}/:/prefs",
                headers=self.headers
            ).json()
            
            return {
                "server_name": identity.get("MediaContainer", {}).get("machineIdentifier"),
                "version": identity.get("MediaContainer", {}).get("version"),
                "platform": identity.get("MediaContainer", {}).get("platform"),
                "friendly_name": prefs.get("MediaContainer", {}).get("FriendlyName"),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def collect_detailed_info(self) -> Dict[str, Any]:
        """Collect detailed Plex information"""
        try:
            detailed = {}
            
            # Libraries
            libraries_resp = requests.get(
                f"{self.base_url}/library/sections",
                headers=self.headers
            )
            if libraries_resp.status_code == 200:
                libraries_data = libraries_resp.json()
                detailed['libraries'] = []
                
                for lib in libraries_data.get("MediaContainer", {}).get("Directory", []):
                    lib_info = {
                        "title": lib.get("title"),
                        "type": lib.get("type"),
                        "key": lib.get("key"),
                        "locations": lib.get("Location", [])
                    }
                    
                    # Get library stats
                    stats_resp = requests.get(
                        f"{self.base_url}/library/sections/{lib['key']}/all",
                        headers=self.headers,
                        params={"X-Plex-Container-Size": 0}
                    )
                    if stats_resp.status_code == 200:
                        stats_data = stats_resp.json()
                        lib_info['item_count'] = stats_data.get("MediaContainer", {}).get("totalSize", 0)
                    
                    detailed['libraries'].append(lib_info)
            
            # Active sessions
            sessions_resp = requests.get(
                f"{self.base_url}/status/sessions",
                headers=self.headers
            )
            if sessions_resp.status_code == 200:
                sessions_data = sessions_resp.json()
                detailed['active_sessions'] = sessions_data.get("MediaContainer", {}).get("size", 0)
            
            return detailed
        except Exception as e:
            return {"error": str(e)}
