#!/usr/bin/env python3
"""Test the documentation generator"""
import sys
sys.path.insert(0, '.')

from homelab_wizard.generators.documentation_generator import DocumentationGenerator

# Test data
test_services = {
    "192.168.1.100": {
        "hostname": "unraid-server",
        "services": [
            {
                "name": "Plex",
                "ports": [32400],
                "confidence": 0.95,
                "device_type": "docker"
            },
            {
                "name": "Radarr", 
                "ports": [7878],
                "confidence": 0.90,
                "device_type": "docker"
            }
        ]
    },
    "192.168.1.101": {
        "hostname": "raspberry-pi",
        "services": [
            {
                "name": "Pi-hole",
                "ports": [80, 53],
                "confidence": 0.98,
                "device_type": "host"
            }
        ]
    }
}

test_configs = {
    "Plex_192.168.1.100": {
        "host": "192.168.1.100",
        "port": 32400,
        "token": "test-token-123"
    },
    "Radarr_192.168.1.100": {
        "host": "192.168.1.100", 
        "port": 7878,
        "api_key": "test-api-key"
    }
}

test_data = {
    "Plex_192.168.1.100": {
        "libraries": ["Movies", "TV Shows", "Music"],
        "total_items": 1500,
        "active_sessions": 2
    }
}

# Generate documentation
print("Testing documentation generator...")
generator = DocumentationGenerator("test_docs")
results = generator.generate_all(test_services, test_configs, test_data)

print(f"\nGenerated {len(results)} documentation files")
print("Check the 'test_docs' directory for output")
