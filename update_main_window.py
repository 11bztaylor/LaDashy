import sys

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Add import for modern service list
if 'from .service_list import ModernServiceList' not in content:
    imports = content.find('from .config_panel import ServiceConfigPanel')
    content = content[:imports] + 'from .service_list import ModernServiceList\n' + content[imports:]

# Replace create_service_list method
old_method_start = content.find('def create_service_list(self, parent):')
old_method_end = content.find('\n    def ', old_method_start + 1)
if old_method_end == -1:
    old_method_end = content.find('\n\n', old_method_start)

new_method = '''def create_service_list(self, parent):
        """Create the modern service selection list"""
        from ..services.definitions import SERVICES
        
        # Create modern service list
        self.service_list = ModernServiceList(
            parent, 
            self.service_vars,
            self.on_service_click,
            self.on_service_toggle
        )
        
        # Add all categories and services
        for category, services in SERVICES.items():
            self.service_list.add_category(category, services)'''

content = content[:old_method_start] + new_method + content[old_method_end:]

# Update on_service_toggle to handle clicks better
old_toggle = content.find('def on_service_toggle(self, service_name):')
if old_toggle != -1:
    toggle_end = content.find('\n    def ', old_toggle + 1)
    new_toggle = '''def on_service_toggle(self, service_name):
        """Handle service checkbox toggle"""
        # Always show config panel when toggled
        self.show_service_config(service_name)
        
    def on_service_click(self, service_name):
        """Handle clicking on service name"""
        # Show config panel without changing checkbox
        self.show_service_config(service_name)
        
    def show_service_config(self, service_name):
        """Show configuration for a service"""
        # Highlight the service
        self.service_list.highlight_service(service_name)
        
        # Find if we have discovered info for this service
        host_info = None
        for ip, info in self.discovered_services.items():
            for service in info.get('services', []):
                if service['name'] == service_name:
                    host_info = {
                        'host': ip,
                        'ports': service.get('ports', []),
                        'hostname': info.get('hostname', 'Unknown')
                    }
                    break
            if host_info:
                break
        
        self.config_panel.show_service_config(service_name, host_info)'''
    
    content = content[:old_toggle] + new_toggle + content[toggle_end:]

# Add method to update service status
status_method = '''
    def update_service_status(self, service_name, status):
        """Update visual status of a service"""
        if hasattr(self, 'service_list'):
            self.service_list.update_service_status(service_name, status)
'''

# Add before generate_docs
generate_pos = content.find('def generate_docs(self):')
content = content[:generate_pos] + status_method + '\n    ' + content[generate_pos:]

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Main window updated with modern UI!")
