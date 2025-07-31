import sys

with open('homelab_wizard/collectors/manager.py', 'r') as f:
    content = f.read()

# Add Sonarr import
if 'from .sonarr_collector' not in content:
    imports = content.find('from .radarr_collector')
    next_line = content.find('\n', imports)
    content = content[:next_line] + '\nfrom .sonarr_collector import SonarrCollector' + content[next_line:]

# Add Sonarr to collectors
if '"Sonarr": SonarrCollector' not in content:
    radarr_line = content.find('"Radarr": RadarrCollector,')
    next_line = content.find('\n', radarr_line)
    content = content[:next_line] + '\n            "Sonarr": SonarrCollector,' + content[next_line:]

with open('homelab_wizard/collectors/manager.py', 'w') as f:
    f.write(content)

print("Added Sonarr collector")
