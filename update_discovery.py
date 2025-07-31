import sys

# Read the main window file
with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Find and update the update_discovered_services method
old_method = '''# Auto-check the service
                if service['name'] in self.service_vars:
                    self.service_vars[service['name']].set(True)'''

new_method = '''# Auto-check the service
                if service['name'] in self.service_vars:
                    self.service_vars[service['name']].set(True)
                    # Show config panel for first service
                    if not hasattr(self, '_first_service_shown'):
                        self._first_service_shown = True
                        host_info = {
                            'host': ip,
                            'ports': service.get('ports', []),
                            'hostname': hostname
                        }
                        self.config_panel.show_service_config(service['name'], host_info)'''

content = content.replace(old_method, new_method)

# Write back
with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Auto-selection feature added!")
