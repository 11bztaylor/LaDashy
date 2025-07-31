import os
import requests
from PIL import Image
import io

# Directory for logos
logo_dir = "homelab_wizard/assets/logos"
os.makedirs(logo_dir, exist_ok=True)

# For demo, let's create simple colored squares as placeholders
# In production, you'd download actual logos
def create_placeholder_logo(name, color):
    img = Image.new('RGB', (32, 32), color=color)
    img.save(os.path.join(logo_dir, f"{name}.png"))

# Create placeholder logos with brand colors
logos = {
    'plex': '#E5A00D',
    'jellyfin': '#00A4DC',
    'emby': '#52B54B',
    'radarr': '#FEC04E',
    'sonarr': '#3FC1C9',
    'prowlarr': '#8A2BE2',
    'nginx': '#009639',
    'pihole': '#F60D1A',
    'portainer': '#13BEF9',
    'default': '#666666'
}

for name, color in logos.items():
    create_placeholder_logo(name, color)

print("Created placeholder logos")
