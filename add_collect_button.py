import sys

with open('homelab_wizard/gui/config_panel.py', 'r') as f:
    content = f.read()

# Add import for collector manager
if 'from ..collectors.manager import CollectorManager' not in content:
    imports = content.find('from ..core.connection_tester import ConnectionTester')
    content = content[:imports] + 'from ..collectors.manager import CollectorManager\n' + content[imports:]

# Initialize collector manager
if 'self.collector_manager = CollectorManager()' not in content:
    init = content.find('self.tester = ConnectionTester()')
    next_line = content.find('\n', init)
    content = content[:next_line] + '\n        self.collector_manager = CollectorManager()' + content[next_line:]

# Add collect button
old_save_button = 'self.save_btn = ttk.Button(button_frame, text="Save Configuration"'
new_buttons = '''# Collect button
        self.collect_btn = ttk.Button(button_frame, text="Collect Data", 
                                     command=self.collect_data, state='disabled')
        self.collect_btn.pack(side='left', padx=(0, 5))
        
        self.save_btn = ttk.Button(button_frame, text="Save Configuration"'''

content = content.replace(old_save_button, new_buttons)

# Enable collect button
old_enable = 'self.test_btn.config(state=\'normal\')'
new_enable = '''self.test_btn.config(state='normal')
        self.collect_btn.config(state='normal')'''
content = content.replace(old_enable, new_enable)

# Add collect_data method
collect_method = '''
    def collect_data(self):
        """Collect data from the service"""
        if not self.current_service:
            return
            
        # Get current config
        config = {}
        for key, var in self.config_vars.items():
            value = var.get()
            if value:
                config[key] = value
                
        # Update status
        self.status_label.config(text="Collecting data...", foreground='blue')
        self.parent.update()
        
        # Collect data
        data = self.collector_manager.collect_service_data(self.current_service, config)
        
        if data.get('status') == 'success':
            # Show summary
            basic = data.get('basic', {})
            detailed = data.get('detailed', {})
            
            summary = f"✓ Data collected! "
            if self.current_service == "Plex" and detailed.get('libraries'):
                summary += f"Found {len(detailed['libraries'])} libraries"
            elif self.current_service == "Radarr" and 'total_movies' in detailed:
                summary += f"Found {detailed['total_movies']} movies"
            
            self.status_label.config(text=summary, foreground='green')
            
            # TODO: Store this data for documentation generation
            print(f"Collected data for {self.current_service}:", data)
        else:
            self.status_label.config(
                text=f"✗ Collection failed: {data.get('error', 'Unknown error')}", 
                foreground='red'
            )
'''

# Insert before get_frame
get_frame_pos = content.find('def get_frame(self):')
content = content[:get_frame_pos] + collect_method + '\n    ' + content[get_frame_pos:]

with open('homelab_wizard/gui/config_panel.py', 'w') as f:
    f.write(content)

print("Collect button added!")
