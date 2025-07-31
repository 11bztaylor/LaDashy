# Add JSON export to the test
import json
from pathlib import Path

test_data = {
    "generated": "2025-07-31T14:23:17",
    "summary": {
        "total_hosts": 2,
        "total_services": 3,
        "configured_services": 2
    },
    "discovered_services": {
        "192.168.1.100": {
            "hostname": "unraid-server",
            "services": [
                {"name": "Plex", "ports": [32400], "confidence": 0.95, "device_type": "docker"},
                {"name": "Radarr", "ports": [7878], "confidence": 0.90, "device_type": "docker"}
            ]
        },
        "192.168.1.101": {
            "hostname": "raspberry-pi",
            "services": [
                {"name": "Pi-hole", "ports": [80, 53], "confidence": 0.98, "device_type": "host"}
            ]
        }
    }
}

# Save to test_docs
Path("test_docs/homelab_data.json").write_text(json.dumps(test_data, indent=2))
print("✅ Created test_docs/homelab_data.json")
