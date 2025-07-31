import sys

with open('homelab_wizard/gui/config_panel.py', 'r') as f:
    content = f.read()

# Add import for connection tester
if 'from ..core.connection_tester' not in content:
    imports = content.find('import os')
    content = content[:imports] + 'from ..core.connection_tester import ConnectionTester\n' + content[imports:]

# Add tester initialization
if 'self.tester = ConnectionTester()' not in content:
    init_section = content.find('self.configs = self.load_configs()')
    content = content[:init_section] + 'self.tester = ConnectionTester()\n        ' + content[init_section:]

# Update save button section to add test button
old_save_button = '''# Save button
        self.save_btn = ttk.Button(self.frame, text="Save Configuration", 
                                  command=self.save_config, state='disabled')
        self.save_btn.pack(side='bottom', pady=(10, 0))'''

new_buttons = '''# Button frame
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        # Test button
        self.test_btn = ttk.Button(button_frame, text="Test Connection", 
                                  command=self.test_connection, state='disabled')
        self.test_btn.pack(side='left', padx=(0, 5))
        
        # Save button
        self.save_btn = ttk.Button(button_frame, text="Save Configuration", 
                                  command=self.save_config, state='disabled')
        self.save_btn.pack(side='left')
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="", foreground='gray')
        self.status_label.pack(side='left', padx=(10, 0))'''

content = content.replace(old_save_button, new_buttons)

# Enable test button in show_service_config
old_enable = 'self.save_btn.config(state=\'normal\')'
new_enable = '''self.save_btn.config(state='normal')
        self.test_btn.config(state='normal')
        self.status_label.config(text='')'''
content = content.replace(old_enable, new_enable)

# Add test_connection method
test_method = '''
    def test_connection(self):
        """Test the current configuration"""
        if not self.current_service:
            return
            
        # Get current config values
        config = {}
        for key, var in self.config_vars.items():
            value = var.get()
            if value:
                config[key] = value
                
        # Update status
        self.status_label.config(text="Testing...", foreground='orange')
        self.parent.update()
        
        # Test connection
        success, message = self.tester.test_connection(self.current_service, config)
        
        if success:
            self.status_label.config(text=f"✓ {message}", foreground='green')
        else:
            self.status_label.config(text=f"✗ {message}", foreground='red')
'''

# Add before get_frame method
get_frame_pos = content.find('def get_frame(self):')
content = content[:get_frame_pos] + test_method + '\n    ' + content[get_frame_pos:]

with open('homelab_wizard/gui/config_panel.py', 'w') as f:
    f.write(content)

print("Test button added!")
