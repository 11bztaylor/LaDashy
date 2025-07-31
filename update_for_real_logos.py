import sys

# Update enhanced_service_list.py
with open('homelab_wizard/gui/enhanced_service_list.py', 'r') as f:
    content = f.read()

# Add PIL import
if 'from PIL import' not in content:
    content = 'from PIL import Image, ImageTk\n' + content

# Replace the emoji icon section with image loading
old_icon_section = '''# Service icon (emoji)
        icon_map = {
            'plex': '🎬', 'jellyfin': '🎭', 'emby': '📺',
            'radarr': '🎦', 'sonarr': '📺', 'prowlarr': '🔍',
            'nginx': '🌐', 'pihole': '🛡️', 'portainer': '🐳',
            'default': '📦'
        }
        icon = icon_map.get(service.get('icon', 'default'), '📦')
        
        icon_label = tk.Label(inner_frame, text=icon, font=('Arial', 16), 
                             bg=self.colors['bg_medium'], fg=self.colors['text_primary'])'''

new_icon_section = '''# Service icon (image or emoji fallback)
        icon_loaded = False
        safe_name = service_name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        logo_path = f"homelab_wizard/assets/logos/{safe_name}.png"
        
        try:
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                icon_label = tk.Label(inner_frame, image=photo, 
                                     bg=self.colors['bg_medium'])
                icon_label.image = photo  # Keep a reference
                icon_loaded = True
        except:
            pass
            
        if not icon_loaded:
            # Fallback to emoji
            icon_map = {
                'plex': '🎬', 'jellyfin': '🎭', 'emby': '📺',
                'radarr': '🎦', 'sonarr': '📺', 'prowlarr': '🔍',
                'nginx': '🌐', 'pihole': '🛡️', 'portainer': '🐳',
                'default': '📦'
            }
            icon = icon_map.get(service.get('icon', 'default'), '📦')
            icon_label = tk.Label(inner_frame, text=icon, font=('Arial', 16), 
                                 bg=self.colors['bg_medium'], fg=self.colors['text_primary'])'''

content = content.replace(old_icon_section, new_icon_section)

# Add os import if not present
if 'import os' not in content:
    content = 'import os\n' + content

with open('homelab_wizard/gui/enhanced_service_list.py', 'w') as f:
    f.write(content)

print("Updated enhanced service list for real logos")

# Also update the modern UI fixed version
with open('homelab_wizard/gui/modern_ui_fixed.py', 'r') as f:
    content = f.read()

# Update the logo path in modern UI
content = content.replace(
    'logo_path = f"homelab_wizard/assets/logos/{icon_name}.png"',
    '''safe_name = self.service_name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        logo_path = f"homelab_wizard/assets/logos/{safe_name}.png"
        if not os.path.exists(logo_path):
            # Try the original icon name
            logo_path = f"homelab_wizard/assets/logos/{icon_name}.png"'''
)

with open('homelab_wizard/gui/modern_ui_fixed.py', 'w') as f:
    f.write(content)

print("Updated modern UI for real logos")
