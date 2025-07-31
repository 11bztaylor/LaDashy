import sys

with open('homelab_wizard/gui/modern_main_window.py', 'r') as f:
    content = f.read()

# Fix the on_service_click method to not use service_list
new_on_service_click = '''def on_service_click(self, service_name):
        """Handle service name click"""
        # Highlight the selected card
        for name, card in self.service_cards.items():
            card.set_selected(name == service_name)
        
        # Find host info if discovered
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
                    
        self.config_panel.show_service_config(service_name, host_info)'''

# Replace the old method
old_start = content.find('def on_service_click(self, service_name):')
if old_start != -1:
    old_end = content.find('\n    def ', old_start + 1)
    if old_end == -1:
        old_end = content.find('\nclass', old_start)
    content = content[:old_start] + new_on_service_click + '\n        \n    ' + content[old_end:]

# Fix the network config dialog issue
content = content.replace(
    'dialog = NetworkConfigDialog(self.root, self.scanner)',
    '''dialog = NetworkConfigDialog(self.root, self.scanner)
        self.root.wait_for_visibility()  # Ensure window is visible before grab'''
)

with open('homelab_wizard/gui/modern_main_window.py', 'w') as f:
    f.write(content)

print("Fixed modern UI")
