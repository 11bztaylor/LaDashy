"""
Base collector class for all services
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import logging

class BaseCollector(ABC):
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Test if connection to service is working"""
        pass
        
    @abstractmethod
    def collect_basic_info(self) -> Dict[str, Any]:
        """Collect basic service information"""
        pass
        
    @abstractmethod
    def collect_detailed_info(self) -> Dict[str, Any]:
        """Collect detailed service information for documentation"""
        pass
        
    def collect_all(self) -> Dict[str, Any]:
        """Collect all available information"""
        try:
            basic = self.collect_basic_info()
            detailed = self.collect_detailed_info()
            return {
                "basic": basic,
                "detailed": detailed,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
