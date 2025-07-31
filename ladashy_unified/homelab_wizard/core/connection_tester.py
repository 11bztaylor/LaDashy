"""
Test connections to services
"""
import requests
import socket
from typing import Dict, Tuple

class ConnectionTester:
    def __init__(self):
        self.timeout = 5
        
    def test_connection(self, service_name: str, config: Dict) -> Tuple[bool, str]:
        """Test connection to a service"""
        # Map service names to test methods
        test_methods = {
            "Plex": self._test_plex,
            "Radarr": self._test_radarr,
            "Sonarr": self._test_sonarr,
            "Prowlarr": self._test_prowlarr,
            "Portainer": self._test_portainer,
            "Pi-hole": self._test_pihole,
        }
        
        if service_name in test_methods:
            return test_methods[service_name](config)
        else:
            # Generic test - just check if port is open
            return self._test_generic(config)
            
    def _test_generic(self, config: Dict) -> Tuple[bool, str]:
        """Generic connection test"""
        host = config.get('host', '')
        port = config.get('port', '')
        
        if not host or not port:
            return False, "Missing host or port"
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            
            if result == 0:
                return True, f"Connected to {host}:{port}"
            else:
                return False, f"Cannot connect to {host}:{port}"
        except Exception as e:
            return False, str(e)
            
    def _test_plex(self, config: Dict) -> Tuple[bool, str]:
        """Test Plex connection"""
        host = config.get('host', '')
        port = config.get('port', '32400')
        token = config.get('token', '')
        
        try:
            url = f"http://{host}:{port}/identity"
            headers = {'X-Plex-Token': token} if token else {}
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return True, "Successfully connected to Plex"
            elif response.status_code == 401:
                return False, "Authentication failed - check token"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
            
    def _test_radarr(self, config: Dict) -> Tuple[bool, str]:
        """Test Radarr connection"""
        host = config.get('host', '')
        port = config.get('port', '7878')
        api_key = config.get('api_key', '')
        base_url = config.get('base_url', '')
        
        try:
            url = f"http://{host}:{port}{base_url}/api/v3/system/status"
            headers = {'X-Api-Key': api_key} if api_key else {}
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return True, "Successfully connected to Radarr"
            elif response.status_code == 401:
                return False, "Authentication failed - check API key"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
            
    def _test_sonarr(self, config: Dict) -> Tuple[bool, str]:
        """Test Sonarr connection"""
        # Similar to Radarr
        config['port'] = config.get('port', '8989')
        return self._test_radarr(config)
        
    def _test_prowlarr(self, config: Dict) -> Tuple[bool, str]:
        """Test Prowlarr connection"""
        host = config.get('host', '')
        port = config.get('port', '9696')
        api_key = config.get('api_key', '')
        
        try:
            url = f"http://{host}:{port}/api/v1/system/status"
            headers = {'X-Api-Key': api_key} if api_key else {}
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return True, "Successfully connected to Prowlarr"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
            
    def _test_portainer(self, config: Dict) -> Tuple[bool, str]:
        """Test Portainer connection"""
        host = config.get('host', '')
        port = config.get('port', '9000')
        
        try:
            url = f"http://{host}:{port}/api/system/status"
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return True, "Successfully connected to Portainer"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
            
    def _test_pihole(self, config: Dict) -> Tuple[bool, str]:
        """Test Pi-hole connection"""
        host = config.get('host', '')
        port = config.get('port', '80')
        
        try:
            url = f"http://{host}:{port}/admin/api.php?status"
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return True, "Successfully connected to Pi-hole"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
