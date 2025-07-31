import sys

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Find the update_discovered_services method and fix it
old_section = """'hostname': hostname"""
new_section = """'hostname': info.get('hostname', 'Unknown')"""

content = content.replace(old_section, new_section)

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed hostname error")
