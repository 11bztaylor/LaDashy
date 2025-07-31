import sys

with open('homelab_wizard/gui/config_panel.py', 'r') as f:
    content = f.read()

# Add import for info panel
if 'from ..gui.service_info_panel' not in content:
    imports = content.find('from ..collectors.manager')
    content = content[:imports] + 'from ..gui.service_info_panel import ServiceInfoPanel\n' + content[imports:]

# Add info panel to setup_ui
setup_ui_end = content.find('def load_configs(self):')
if 'self.info_panel' not in content[:setup_ui_end]:
    # Find where to add the info panel
    status_label_section = content.find('self.status_label.pack(side=\'left\', padx=(10, 0))')
    if status_label_section != -1:
        next_line = content.find('\n', status_label_section)
        info_panel_code = '''
        
        # Add separator
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=(15, 0))
        
        # Info panel
        self.info_panel = ServiceInfoPanel(self.frame, bg_color='#f0f0f0')
        self.info_panel.get_frame().pack(fill='both', expand=True)'''
        
        content = content[:next_line] + info_panel_code + content[next_line:]

# Update test_connection to show info on success
test_success = content.find('self.status_label.config(text=f"✓ {message}", foreground=\'green\')')
if test_success != -1:
    next_line = content.find('\n', test_success)
    show_info_code = '''
            # Show service info on successful connection
            self.info_panel.show_service_info(self.current_service, config, self.collector_manager)'''
    content = content[:next_line] + show_info_code + content[next_line:]

with open('homelab_wizard/gui/config_panel.py', 'w') as f:
    f.write(content)

print("Updated config panel with info display")
