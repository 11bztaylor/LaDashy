import sys
# Read the main window file
with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Add import for config panel
if 'from .config_panel import ServiceConfigPanel' not in content:
    import_section = content.find('from .scan_dialog import ScanProgressDialog')
    if import_section != -1:
        content = content[:import_section] + 'from .config_panel import ServiceConfigPanel\n' + content[import_section:]

# Add config panel to setup_gui
if 'self.config_panel' not in content:
    setup_gui_section = content.find('def create_services_tab(self):')
    if setup_gui_section != -1:
        # Find the services_frame creation
        services_frame_section = content.find('services_frame = ttk.Frame(self.notebook)', setup_gui_section)
        if services_frame_section != -1:
            # Replace the services tab creation
            new_services_tab = '''def create_services_tab(self):
        """Create services selection tab with config panel"""
        services_frame = ttk.Frame(self.notebook)
        self.notebook.add(services_frame, text="Services")
        
        # Create main container with two panels
        main_container = ttk.Frame(services_frame)
        main_container.pack(fill='both', expand=True)
        
        # Left panel for services
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Right panel for configuration
        self.config_panel = ServiceConfigPanel(main_container)
        self.config_panel.get_frame().pack(side='right', fill='both', padx=(10, 0))
        
        # Control buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill='x', pady=10)
        
        ttk.Button(control_frame, text="🔍 Scan Network",
                  command=self.scan_network).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="⚙️ Configure Networks",
                  command=self.configure_networks).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Select All",
                  command=self.select_all).pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Clear All",
                  command=self.clear_all).pack(side='left', padx=5)
        
        # Services list
        self.create_service_list(left_panel)'''
            
            # Replace the method
            method_end = content.find('\n    def ', setup_gui_section + 1)
            content = content[:setup_gui_section] + new_services_tab + content[method_end:]

# Update create_service_list to handle clicks
if '<<CheckboxToggled>>' not in content:
    # Add checkbox click handler
    handler_code = '''
    def on_service_toggle(self, service_name):
        """Handle service checkbox toggle"""
        if self.service_vars[service_name].get():
            # Service was checked - show config
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
    
    # Find where to add it
    select_all_pos = content.find('def select_all(self):')
    if select_all_pos != -1:
        content = content[:select_all_pos] + handler_code + '\n    ' + content[select_all_pos:]

# Update checkbox creation to add command
old_checkbox = 'cb = ttk.Checkbutton(cat_frame, text=service["name"], variable=var)'
new_checkbox = '''cb = ttk.Checkbutton(cat_frame, text=service["name"], variable=var,
                                    command=lambda s=service["name"]: self.on_service_toggle(s))'''
content = content.replace(old_checkbox, new_checkbox)

# Write the updated file
with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Main window updated successfully!")
