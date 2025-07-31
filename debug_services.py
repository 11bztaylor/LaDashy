from homelab_wizard.services.definitions import SERVICES

print("Services structure:")
for category, services in SERVICES.items():
    print(f"\n{category}:")
    for service in services:
        print(f"  - {service}")
