"""Collector for Portainer Docker management"""
import requests
from typing import Dict, Any, Optional
from .base_collector import BaseCollector

class PortainerCollector(BaseCollector):
    """Collector for Portainer Docker management"""
    
    def __init__(self):
        super().__init__()
        self.name = "Portainer"
        self.default_port = 9000
        
    def test_connection(self, host: str, port: int, config: Dict[str, Any]) -> bool:
        """Test connection to Portainer"""
        try:
            response = self.session.get(
                f"http://{host}:{port}/api/status",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Portainer connection failed: {e}")
            return False
    
    def collect_basic_info(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect basic Portainer information"""
        try:
            response = self.session.get(
                f"http://{host}:{port}/api/status",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'version': data.get('Version', 'Unknown'),
                    'instance_id': data.get('InstanceID', 'Unknown')
                }
        except Exception as e:
            self.logger.error(f"Failed to collect Portainer info: {e}")
        
        return {}
    
    def collect_detailed_info(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect detailed Portainer information (requires authentication)"""
        username = config.get('username')
        password = config.get('password')
        
        if not username or not password:
            return {'error': 'Username and password required for detailed information'}
        
        try:
            # Authenticate
            auth_response = self.session.post(
                f"http://{host}:{port}/api/auth",
                json={'Username': username, 'Password': password},
                timeout=self.timeout
            )
            
            if auth_response.status_code != 200:
                return {'error': 'Authentication failed'}
            
            token = auth_response.json().get('jwt')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get endpoints
            endpoints_response = self.session.get(
                f"http://{host}:{port}/api/endpoints",
                headers=headers,
                timeout=self.timeout
            )
            
            detailed_info = {}
            
            if endpoints_response.status_code == 200:
                endpoints = endpoints_response.json()
                detailed_info['total_endpoints'] = len(endpoints)
                detailed_info['endpoints'] = []
                
                for endpoint in endpoints[:3]:  # Limit to first 3 endpoints
                    endpoint_info = {
                        'name': endpoint.get('Name'),
                        'type': endpoint.get('Type'),
                        'status': endpoint.get('Status')
                    }
                    detailed_info['endpoints'].append(endpoint_info)
            
            return detailed_info
            
        except Exception as e:
            self.logger.error(f"Failed to collect detailed Portainer info: {e}")
            return {'error': str(e)}
