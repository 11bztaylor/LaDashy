"""Collector for Jellyfin media server"""
import requests
from typing import Dict, Any, Optional
from .base_collector import BaseCollector

class JellyfinCollector(BaseCollector):
    """Collector for Jellyfin media server"""
    
    def __init__(self):
        super().__init__()
        self.name = "Jellyfin"
        self.default_port = 8096
        
    def test_connection(self, host: str, port: int, config: Dict[str, Any]) -> bool:
        """Test connection to Jellyfin"""
        try:
            # Jellyfin public endpoint
            response = self.session.get(
                f"http://{host}:{port}/System/Info/Public",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Jellyfin connection failed: {e}")
            return False
    
    def collect_basic_info(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect basic Jellyfin information"""
        try:
            # Get public system info
            response = self.session.get(
                f"http://{host}:{port}/System/Info/Public",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'server_name': data.get('ServerName', 'Unknown'),
                    'version': data.get('Version', 'Unknown'),
                    'operating_system': data.get('OperatingSystem', 'Unknown'),
                    'id': data.get('Id', 'Unknown')
                }
        except Exception as e:
            self.logger.error(f"Failed to collect Jellyfin info: {e}")
        
        return {}
    
    def collect_detailed_info(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect detailed Jellyfin information (requires API key)"""
        api_key = config.get('api_key')
        if not api_key:
            return {'error': 'API key required for detailed information'}
        
        try:
            headers = {'X-Emby-Token': api_key}
            
            # Get library information
            libraries_response = self.session.get(
                f"http://{host}:{port}/Library/VirtualFolders",
                headers=headers,
                timeout=self.timeout
            )
            
            detailed_info = {}
            
            if libraries_response.status_code == 200:
                libraries = libraries_response.json()
                detailed_info['libraries'] = []
                for lib in libraries:
                    detailed_info['libraries'].append({
                        'name': lib.get('Name'),
                        'path': lib.get('Locations', ['Unknown'])[0] if lib.get('Locations') else 'Unknown',
                        'type': lib.get('CollectionType', 'Unknown')
                    })
                detailed_info['total_libraries'] = len(libraries)
            
            return detailed_info
            
        except Exception as e:
            self.logger.error(f"Failed to collect detailed Jellyfin info: {e}")
            return {'error': str(e)}
