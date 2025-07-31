import sys

with open('homelab_wizard/gui/modern_ui_fixed.py', 'r') as f:
    content = f.read()

# Load saved configs in ModernConfigPanel init
init_section = content.find('def __init__(self, parent, **kwargs):')
if init_section != -1:
    collector_init = content.find('self.collector_manager = CollectorManager()', init_section)
    if collector_init != -1:
        next_line = content.find('\n', collector_init)
        load_configs = '''
        
        # Load saved configurations
        self.load_saved_configs()'''
        content = content[:next_line] + load_configs + content[next_line:]

# Add method to load configs
if 'def load_saved_configs(self):' not in content:
    class_end = content.find('\nclass', content.find('class ModernConfigPanel'))
    if class_end == -1:
        class_end = len(content)
    
    load_method = '''
    
    def load_saved_configs(self):
        """Load previously saved configurations"""
        import os
        import json
        
        config_file = os.path.expanduser("~/.ladashy/service_configs.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.saved_configs = json.load(f)
                    
                # Notify parent window about configured services
                parent = self.master
                while parent and not hasattr(parent, 'mark_configured_services'):
                    parent = getattr(parent, 'master', None)
                    
                if parent and hasattr(parent, 'mark_configured_services'):
                    configured_services = set()
                    for key in self.saved_configs:
                        service_name = key.split('_')[0]
                        configured_services.add(service_name)
                    parent.mark_configured_services(configured_services)
            except:
                self.saved_configs = {}
        else:
            self.saved_configs = {}'''
    
    insert_pos = content.rfind('\n', 0, class_end)
    content = content[:insert_pos] + load_method + content[insert_pos:]

with open('homelab_wizard/gui/modern_ui_fixed.py', 'w') as f:
    f.write(content)

# Now update main window to mark configured services
with open('homelab_wizard/gui/modern_main_window.py', 'r') as f:
    content = f.read()

# Add method to mark configured services
if 'def mark_configured_services' not in content:
    run_pos = content.find('def run(self):')
    if run_pos != -1:
        mark_method = '''def mark_configured_services(self, service_names):
        """Mark services as configured"""
        for service_name in service_names:
            if service_name in self.service_cards:
                self.service_cards[service_name].set_status('configured')
    
    '''
        content = content[:run_pos] + mark_method + content[run_pos:]

with open('homelab_wizard/gui/modern_main_window.py', 'w') as f:
    f.write(content)

print("Added configuration indicators")
