"""Collector for Pi-hole DNS ad blocker"""
import requests
from typing import Dict, Any, Optional
from .base_collector import BaseCollector

class PiholeCollector(BaseCollector):
    """Collector for Pi-hole DNS ad blocker"""
    
    def __init__(self):
        super().__init__()
        self.name = "Pi-hole"
        self.default_port = 80
        
    def test_connection(self, host: str, port: int, config: Dict[str, Any]) -> bool:
        """Test connection to Pi-hole"""
        try:
            response = self.session.get(
                f"http://{host}:{port}/admin/api.php?status",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Pi-hole connection failed: {e}")
            return False
    
    def collect_basic_info(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect basic Pi-hole information"""
        try:
            # Get status
            status_response = self.session.get(
                f"http://{host}:{port}/admin/api.php?status",
                timeout=self.timeout
            )
            
            # Get version
            version_response = self.session.get(
                f"http://{host}:{port}/admin/api.php?version",
                timeout=self.timeout
            )
            
            basic_info = {}
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                basic_info['status'] = status_data.get('status', 'Unknown')
            
            if version_response.status_code == 200:
                version_data = version_response.json()
                basic_info['core_version'] = version_data.get('core_current', 'Unknown')
                basic_info['web_version'] = version_data.get('web_current', 'Unknown')
                basic_info['ftl_version'] = version_data.get('FTL_current', 'Unknown')
            
            return basic_info
            
        except Exception as e:
            self.logger.error(f"Failed to collect Pi-hole info: {e}")
        
        return {}
    
    def collect_detailed_info(self, host: str, port: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect detailed Pi-hole statistics"""
        try:
            # Get summary stats (doesn't require auth for basic stats)
            summary_response = self.session.get(
                f"http://{host}:{port}/admin/api.php?summary",
                timeout=self.timeout
            )
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                return {
                    'domains_blocked': data.get('domains_being_blocked', 0),
                    'dns_queries_today': data.get('dns_queries_today', 0),
                    'ads_blocked_today': data.get('ads_blocked_today', 0),
                    'ads_percentage_today': data.get('ads_percentage_today', 0),
                    'unique_domains': data.get('unique_domains', 0),
                    'queries_forwarded': data.get('queries_forwarded', 0),
                    'queries_cached': data.get('queries_cached', 0),
                    'clients_ever_seen': data.get('clients_ever_seen', 0),
                    'unique_clients': data.get('unique_clients', 0),
                    'status': data.get('status', 'Unknown')
                }
            
        except Exception as e:
            self.logger.error(f"Failed to collect detailed Pi-hole info: {e}")
            
        return {}
