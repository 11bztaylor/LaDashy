import sys

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Make sure on_service_click is properly defined
if 'def on_service_click' not in content:
    # Add it after on_service_toggle
    toggle_pos = content.find('def on_service_toggle')
    if toggle_pos != -1:
        next_method = content.find('\n    def ', toggle_pos + 1)
        if next_method == -1:
            next_method = len(content)
        
        new_methods = '''def on_service_toggle(self, service_name):
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
        if hasattr(self, 'service_list'):
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
        
        self.config_panel.show_service_config(service_name, host_info)
        
    '''
        
        content = content[:toggle_pos] + new_methods + content[next_method:]

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed enhanced UI click handling")
