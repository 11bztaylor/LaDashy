# Quick test to ensure HTML dashboard is created
from homelab_wizard.generators.documentation_generator import DocumentationGenerator

# Use the same test data
test_services = {
    "192.168.1.100": {
        "hostname": "unraid-server", 
        "services": [
            {"name": "Plex", "ports": [32400], "confidence": 0.95, "device_type": "docker"}
        ]
    }
}

gen = DocumentationGenerator("test_docs_fixed")
gen.export_to_html_dashboard(test_services, {})
print("Check test_docs_fixed/dashboard.html")
