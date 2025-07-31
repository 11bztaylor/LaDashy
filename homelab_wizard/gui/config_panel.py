"""
Service configuration panel for connection details
"""
import tkinter as tk
from tkinter import ttk
import json
from ..gui.service_info_panel import ServiceInfoPanel
from ..collectors.manager import CollectorManager
from ..core.connection_tester import ConnectionTester
import os

class ServiceConfigPanel:
    def __init__(self, parent):
        self.parent = parent
        self.current_service = None
        self.config_vars = {}
        self.tester = ConnectionTester()
        self.collector_manager = CollectorManager()
        self.configs = self.load_configs()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the configuration panel UI"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Service Configuration", padding=10)
        
        # Service name label
        self.service_label = ttk.Label(self.frame, text="Select a service to configure", 
                                      font=('Arial', 12, 'bold'))
        self.service_label.pack(pady=(0, 10))
        
        # Config container
        self.config_container = ttk.Frame(self.frame)
        self.config_container.pack(fill='both', expand=True)
        
        # Button frame
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        # Test button
        self.test_btn = ttk.Button(button_frame, text="Test Connection", 
                                  command=self.test_connection, state='disabled')
        self.test_btn.pack(side='left', padx=(0, 5))
        
        # Save button
        # Collect button
        self.collect_btn = ttk.Button(button_frame, text="Collect Data", 
                                     command=self.collect_data, state='disabled')
        self.collect_btn.pack(side='left', padx=(0, 5))
        
        self.save_btn = ttk.Button(button_frame, text="Save Configuration", 
                                  command=self.save_config, state='disabled')
        self.save_btn.pack(side='left')
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="", foreground='gray')
        self.status_label.pack(side='left', padx=(10, 0))
        
        # Add separator
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=(15, 0))
        
        # Info panel
        self.info_panel = ServiceInfoPanel(self.frame, bg_color='#f0f0f0')
        self.info_panel.get_frame().pack(fill='both', expand=True)
        
    def load_configs(self):
        """Load saved configurations"""
        config_file = os.path.expanduser("~/.ladashy/service_configs.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_configs(self):
        """Save configurations to file"""
        config_dir = os.path.expanduser("~/.ladashy")
        os.makedirs(config_dir, exist_ok=True)
        
        config_file = os.path.join(config_dir, "service_configs.json")
        with open(config_file, 'w') as f:
            json.dump(self.configs, f, indent=2)
            
    def show_service_config(self, service_name, host_info=None):
        """Show configuration for a specific service"""
        self.current_service = service_name
        self.service_label.config(text=f"Configure: {service_name}")
        self.save_btn.config(state='normal')
        self.test_btn.config(state='normal')
        self.collect_btn.config(state='normal')
        self.status_label.config(text='')
        
        # Clear current config
        for widget in self.config_container.winfo_children():
            widget.destroy()
        self.config_vars.clear()
        
        # Get service requirements
        requirements = self.get_service_requirements(service_name)
        
        # Create input fields
        for req in requirements:
            field_frame = ttk.Frame(self.config_container)
            field_frame.pack(fill='x', pady=5)
            
            ttk.Label(field_frame, text=f"{req['label']}:").pack(side='left', padx=(0, 10))
            
            var = tk.StringVar()
            self.config_vars[req['key']] = var
            
            # Load saved value or use discovered info
            saved_key = f"{service_name}_{host_info['host'] if host_info else 'default'}"
            if saved_key in self.configs and req['key'] in self.configs[saved_key]:
                var.set(self.configs[saved_key][req['key']])
            elif host_info and req['key'] == 'host':
                var.set(host_info['host'])
            elif host_info and req['key'] == 'port' and host_info.get('ports'):
                var.set(str(host_info['ports'][0]))
            
            if req['type'] == 'password':
                entry = ttk.Entry(field_frame, textvariable=var, show='*', width=30)
            else:
                entry = ttk.Entry(field_frame, textvariable=var, width=30)
            entry.pack(side='left', fill='x', expand=True)
            
            if req.get('hint'):
                hint_label = ttk.Label(field_frame, text=f"({req['hint']})", 
                                      font=('Arial', 9), foreground='gray')
                hint_label.pack(side='left', padx=(5, 0))
                
    def get_service_requirements(self, service_name):
        """Get configuration requirements for a service"""
        # Define requirements for each service
        service_reqs = {
            "Plex": [
                {"key": "host", "label": "Host/IP", "type": "text", "hint": "e.g., 192.168.1.100"},
                {"key": "port", "label": "Port", "type": "text", "hint": "default: 32400"},
                {"key": "token", "label": "Token", "type": "password", "hint": "X-Plex-Token"},
            ],
            "Radarr": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text", "hint": "default: 7878"},
                {"key": "api_key", "label": "API Key", "type": "password"},
                {"key": "base_url", "label": "Base URL", "type": "text", "hint": "optional, e.g., /radarr"},
            ],
            "Sonarr": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text", "hint": "default: 8989"},
                {"key": "api_key", "label": "API Key", "type": "password"},
                {"key": "base_url", "label": "Base URL", "type": "text", "hint": "optional, e.g., /sonarr"},
            ],
            "Prowlarr": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text", "hint": "default: 9696"},
                {"key": "api_key", "label": "API Key", "type": "password"},
            ],
            "Portainer": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text", "hint": "default: 9000"},
                {"key": "username", "label": "Username", "type": "text"},
                {"key": "password", "label": "Password", "type": "password"},
            ],
            "Pi-hole": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text", "hint": "default: 80"},
                {"key": "api_token", "label": "API Token", "type": "password", "hint": "from Settings > API"},
            ],
        }
        
        # Default for unknown services
        default = [
            {"key": "host", "label": "Host/IP", "type": "text"},
            {"key": "port", "label": "Port", "type": "text"},
            {"key": "username", "label": "Username", "type": "text", "hint": "if required"},
            {"key": "password", "label": "Password", "type": "password", "hint": "if required"},
        ]
        
        return service_reqs.get(service_name, default)
        
    def save_config(self):
        """Save current configuration"""
        if not self.current_service:
            return
            
        # Get host from config
        host = self.config_vars.get('host', tk.StringVar()).get() or 'default'
        config_key = f"{self.current_service}_{host}"
        
        # Save all values
        self.configs[config_key] = {}
        for key, var in self.config_vars.items():
            value = var.get()
            if value:  # Only save non-empty values
                self.configs[config_key][key] = value
                
        self.save_configs()
        
        # Show success
        self.service_label.config(text=f"✓ {self.current_service} configuration saved!")
        
        # Mark as configured in main window
        try:
                main_window = self.parent
                while main_window and not hasattr(main_window, 'update_service_status'):
                    main_window = getattr(main_window, 'master', None)
        except:
                main_window = None
        if hasattr(main_window, 'update_service_status'):
            main_window.update_service_status(self.current_service, 'configured')
        self.parent.after(2000, lambda: self.service_label.config(text=f"Configure: {self.current_service}"))

    
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
            # Show service info on successful connection
            self.info_panel.show_service_info(self.current_service, config, self.collector_manager)
            # Notify main window
            # Navigate up to main window - handle different widget hierarchies
            try:
                # Try different paths to find main window
                main_window = self.parent
                while main_window and not hasattr(main_window, 'update_service_status'):
                    main_window = getattr(main_window, 'master', None)
            except:
                main_window = None
            if hasattr(main_window, 'update_service_status'):
                main_window.update_service_status(self.current_service, 'connected')
        else:
            self.status_label.config(text=f"✗ {message}", foreground='red')
            # Notify main window
            # Navigate up to main window - handle different widget hierarchies
            try:
                # Try different paths to find main window
                main_window = self.parent
                while main_window and not hasattr(main_window, 'update_service_status'):
                    main_window = getattr(main_window, 'master', None)
            except:
                main_window = None
            if hasattr(main_window, 'update_service_status'):
                main_window.update_service_status(self.current_service, 'error')

    
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

    def get_frame(self):
        """Get the panel frame"""
        return self.frame
