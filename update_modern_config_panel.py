import sys

with open('homelab_wizard/gui/modern_ui_fixed.py', 'r') as f:
    content = f.read()

# Add import for service info panel
if 'from ..gui.service_info_panel' not in content:
    imports_section = content.find('from ..collectors.manager import CollectorManager')
    if imports_section != -1:
        content = content[:imports_section] + 'from ..gui.service_info_panel import ServiceInfoPanel\n' + content[imports_section:]

# Find the ModernConfigPanel class and add info panel
class_start = content.find('class ModernConfigPanel(ctk.CTkFrame):')
if class_start != -1:
    # Add info panel to __init__
    init_end = content.find('self.setup_ui()', class_start)
    if init_end != -1 and 'self.saved_configs = {}' not in content:
        init_end = content.find('\n', init_end)
        new_init = '''
        
        # Track saved configurations
        self.saved_configs = {}'''
        content = content[:init_end] + new_init + content[init_end:]
    
    # Update setup_ui to include info panel
    setup_ui_section = content.find('def setup_ui(self):', class_start)
    if setup_ui_section != -1:
        # Find where buttons are created
        button_section = content.find('self.save_btn.pack(side="left", padx=5)', setup_ui_section)
        if button_section != -1:
            next_line = content.find('\n', button_section)
            info_panel_code = '''
        
        # Separator
        separator = ctk.CTkFrame(self, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", padx=20, pady=(20, 10))
        
        # Service info panel
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create custom info panel for modern UI
        self.info_title = ctk.CTkLabel(
            info_frame,
            text="Service Information",
            font=("Arial", 16, "bold")
        )
        self.info_title.pack(pady=(0, 10))
        
        self.info_container = ctk.CTkScrollableFrame(
            info_frame,
            fg_color=("gray90", "gray20"),
            corner_radius=8
        )
        self.info_container.pack(fill="both", expand=True)
        
        self.info_status = ctk.CTkLabel(
            info_frame,
            text="Connect to a service to see information",
            font=("Arial", 12),
            text_color=("gray60", "gray40")
        )
        self.info_status.pack(pady=(10, 0))'''
            content = content[:next_line] + info_panel_code + content[next_line:]

# Update show_service_config to show saved indicator
show_config_method = content.find('def show_service_config(self, service_name, host_info=None):')
if show_config_method != -1:
    # Find where we set values
    set_value_section = content.find('var.set(host_info[\'host\'])', show_config_method)
    if set_value_section != -1:
        # Add check for saved configs before that section
        check_start = content.rfind('# Pre-fill values', show_config_method, set_value_section)
        if check_start != -1:
            new_prefill = '''# Pre-fill values
            config_key = f"{service_name}_{host_info['host'] if host_info else 'default'}"
            has_saved_config = config_key in self.saved_configs'''
            content = content[:check_start] + new_prefill + '\n            ' + content[check_start + len('# Pre-fill values'):]

# Add visual indicator for saved configs
entry_section = content.find('entry = ctk.CTkEntry(frame, textvariable=var, show="*", width=250)')
if entry_section != -1:
    new_entry = '''entry = ctk.CTkEntry(frame, textvariable=var, show="*", width=250)
                # Show indicator if password is saved
                if has_saved_config and req['key'] in self.saved_configs.get(config_key, {}) and self.saved_configs[config_key][req['key']]:
                    entry.configure(placeholder_text="••••••••")'''
    content = content.replace(
        'entry = ctk.CTkEntry(frame, textvariable=var, show="*", width=250)',
        new_entry
    )

# Update test_connection to show info
test_method = content.find('def test_connection(self):')
if test_method != -1:
    success_section = content.find('self.status_label.configure(text=f"✓ {message}", text_color="green")', test_method)
    if success_section != -1:
        next_line = content.find('\n', success_section)
        show_info = '''
            # Show service information
            self._display_service_info()'''
        content = content[:next_line] + show_info + content[next_line:]

# Update save_config to track saved configs
save_method = content.find('def save_config(self):')
if save_method != -1:
    save_section = content.find('self.status_label.configure(text="✓ Configuration saved!", text_color="green")', save_method)
    if save_section != -1:
        # Add before status update
        track_section = content.rfind('config =', save_method, save_section)
        if track_section != -1:
            new_save = '''config = {}
        for key, var in self.config_vars.items():
            value = var.get()
            if value:
                config[key] = value
        
        # Track saved configuration
        config_key = f"{self.current_service}_{config.get('host', 'default')}"
        self.saved_configs[config_key] = config.copy()
        
        # Save to file as well
        import os
        import json
        config_dir = os.path.expanduser("~/.ladashy")
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "service_configs.json")
        
        try:
            # Load existing configs
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    all_configs = json.load(f)
            else:
                all_configs = {}
            
            # Update with new config
            all_configs[config_key] = config
            
            # Save back
            with open(config_file, 'w') as f:
                json.dump(all_configs, f, indent=2)
        except:
            pass
            '''
        
        # Replace the section
        end_of_config = content.find('\n', track_section)
        content = content[:track_section] + new_save + '\n        ' + content[end_of_config:]

# Add method to display service info
if '_display_service_info' not in content:
    # Add before the last method or at the end of class
    class_end = content.find('\nclass', class_start + 1)
    if class_end == -1:
        class_end = len(content)
    
    display_method = '''
    
    def _display_service_info(self):
        """Display service information after connection"""
        if not self.current_service:
            return
            
        # Clear previous info
        for widget in self.info_container.winfo_children():
            widget.destroy()
            
        self.info_status.configure(text="Loading information...", text_color=("gray60", "gray40"))
        
        # Get config
        config = {}
        for key, var in self.config_vars.items():
            value = var.get()
            if value:
                config[key] = value
        
        # Start thread to collect data
        import threading
        thread = threading.Thread(
            target=self._collect_and_display,
            args=(config,)
        )
        thread.daemon = True
        thread.start()
    
    def _collect_and_display(self, config):
        """Collect and display service data"""
        try:
            data = self.collector_manager.collect_service_data(self.current_service, config)
            
            if data.get('status') == 'success':
                self.after(0, self._update_info_display, data)
            else:
                self.after(0, lambda: self.info_status.configure(
                    text=f"✗ Error: {data.get('error', 'Unknown error')}",
                    text_color="red"
                ))
        except Exception as e:
            self.after(0, lambda: self.info_status.configure(
                text=f"✗ Error: {str(e)}",
                text_color="red"
            ))
    
    def _update_info_display(self, data):
        """Update the info display with collected data"""
        basic = data.get('basic', {})
        detailed = data.get('detailed', {})
        
        # Clear container
        for widget in self.info_container.winfo_children():
            widget.destroy()
        
        # Display based on service type
        if self.current_service == "Plex":
            self._display_plex_info(basic, detailed)
        elif self.current_service == "Radarr":
            self._display_radarr_info(basic, detailed)
        elif self.current_service == "Sonarr":
            self._display_sonarr_info(basic, detailed)
        else:
            self._display_generic_info(basic, detailed)
            
        self.info_status.configure(text="✓ Information loaded", text_color="green")
    
    def _add_info_row(self, label, value, parent=None):
        """Add an information row"""
        if parent is None:
            parent = self.info_container
            
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=2)
        
        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=("Arial", 12, "bold"),
            width=120,
            anchor="w"
        )
        label_widget.pack(side="left")
        
        value_widget = ctk.CTkLabel(
            row,
            text=str(value),
            font=("Arial", 12),
            anchor="w"
        )
        value_widget.pack(side="left", fill="x", expand=True)
    
    def _display_plex_info(self, basic, detailed):
        """Display Plex information"""
        if basic.get('version'):
            self._add_info_row("Version:", basic['version'])
        if basic.get('platform'):
            self._add_info_row("Platform:", basic['platform'])
            
        if detailed.get('libraries'):
            # Libraries section
            lib_label = ctk.CTkLabel(
                self.info_container,
                text="Libraries:",
                font=("Arial", 13, "bold")
            )
            lib_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            for lib in detailed['libraries']:
                lib_text = f"{lib['title']} ({lib['type']}): {lib.get('item_count', 0)} items"
                lib_row = ctk.CTkLabel(
                    self.info_container,
                    text=f"  • {lib_text}",
                    font=("Arial", 11)
                )
                lib_row.pack(anchor="w", padx=20)
                
        if 'active_sessions' in detailed:
            self._add_info_row("Active Streams:", detailed['active_sessions'])
    
    def _display_radarr_info(self, basic, detailed):
        """Display Radarr information"""
        if basic.get('version'):
            self._add_info_row("Version:", basic['version'])
            
        if 'total_movies' in detailed:
            self._add_info_row("Total Movies:", detailed['total_movies'])
        if 'monitored_movies' in detailed:
            self._add_info_row("Monitored:", detailed['monitored_movies'])
        if 'downloaded_movies' in detailed:
            self._add_info_row("Downloaded:", detailed['downloaded_movies'])
        if 'queue_count' in detailed:
            self._add_info_row("In Queue:", detailed['queue_count'])
    
    def _display_sonarr_info(self, basic, detailed):
        """Display Sonarr information"""
        if basic.get('version'):
            self._add_info_row("Version:", basic['version'])
            
        if 'total_series' in detailed:
            self._add_info_row("Total Series:", detailed['total_series'])
        if 'monitored_series' in detailed:
            self._add_info_row("Monitored:", detailed['monitored_series'])
        if 'total_episodes' in detailed:
            self._add_info_row("Total Episodes:", detailed['total_episodes'])
        if 'downloaded_episodes' in detailed:
            self._add_info_row("Downloaded:", detailed['downloaded_episodes'])
    
    def _display_generic_info(self, basic, detailed):
        """Display generic information"""
        for key, value in basic.items():
            if key != 'error':
                label = key.replace('_', ' ').title() + ":"
                self._add_info_row(label, value)'''
    
    # Insert before class end
    insert_pos = content.rfind('\n', 0, class_end)
    content = content[:insert_pos] + display_method + content[insert_pos:]

with open('homelab_wizard/gui/modern_ui_fixed.py', 'w') as f:
    f.write(content)

print("Updated modern config panel with info display")
