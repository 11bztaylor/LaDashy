"""
Fixed modern UI components using customtkinter
"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernServiceCard(ctk.CTkFrame):
    def __init__(self, parent, service_name, icon_name, on_click, on_toggle, **kwargs):
        super().__init__(parent, corner_radius=10, height=50, **kwargs)
        
        self.service_name = service_name
        self.on_click = on_click
        self.on_toggle = on_toggle
        self.is_selected = False
        self.checkbox_var = tk.BooleanVar()
        
        # Configure grid - remove the problematic column
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Container frame for better alignment
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Checkbox
        self.checkbox = ctk.CTkCheckBox(
            container, 
            text="",
            variable=self.checkbox_var,
            width=28,
            checkbox_width=20,
            checkbox_height=20,
            command=self._on_checkbox_toggle
        )
        self.checkbox.pack(side="left", padx=(0, 5))
        
        # Try to load logo
        safe_name = self.service_name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        logo_path = f"homelab_wizard/assets/logos/{safe_name}.png"
        if not os.path.exists(logo_path):
            # Try the original icon name
            logo_path = f"homelab_wizard/assets/logos/{icon_name}.png"
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((24, 24), Image.Resampling.LANCZOS)
                self.logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(24, 24))
                logo_label = ctk.CTkLabel(container, image=self.logo, text="")
                logo_label.pack(side="left", padx=(0, 8))
            except:
                # Fallback to emoji
                self._add_emoji_icon(container, icon_name)
        else:
            self._add_emoji_icon(container, icon_name)
        
        # Service name
        self.name_label = ctk.CTkLabel(
            container,
            text=service_name,
            font=("Arial", 14),
            anchor="w",
            cursor="hand2"
        )
        self.name_label.pack(side="left", fill="x", expand=True)
        self.name_label.bind("<Button-1>", lambda e: self._on_name_click())
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            container,
            text="",
            font=("Arial", 16),
            width=30
        )
        self.status_label.pack(side="right", padx=(5, 0))
        
        # Configure hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _add_emoji_icon(self, parent, icon_name):
        """Add emoji icon as fallback"""
        icons = {
            "plex": "🎬", "jellyfin": "🎭", "emby": "📺",
            "radarr": "🎦", "sonarr": "📺", "prowlarr": "🔍",
            "nginx": "🌐", "pihole": "🛡️", "portainer": "🐳",
            "default": "📦"
        }
        emoji = icons.get(icon_name, "📦")
        emoji_label = ctk.CTkLabel(parent, text=emoji, font=("Arial", 18))
        emoji_label.pack(side="left", padx=(0, 8))
        
    def _on_enter(self, event):
        if not self.is_selected:
            self.configure(fg_color=("gray85", "gray25"))
            
    def _on_leave(self, event):
        if not self.is_selected:
            self.configure(fg_color=("gray92", "gray14"))
            
    def _on_checkbox_toggle(self):
        self.on_toggle(self.service_name, self.checkbox_var.get())
        
    def _on_name_click(self):
        self.on_click(self.service_name)
        self.set_selected(True)
        
    def set_selected(self, selected):
        self.is_selected = selected
        if selected:
            self.configure(fg_color=("gray80", "gray30"))
        else:
            self.configure(fg_color=("gray92", "gray14"))
            
    def set_status(self, status):
        """Update status indicator"""
        if status == 'connected':
            self.status_label.configure(text="✓", text_color="green")
        elif status == 'error':
            self.status_label.configure(text="✗", text_color="red")
        elif status == 'configured':
            self.status_label.configure(text="●", text_color="orange")
        else:
            self.status_label.configure(text="")
            
    def set_checked(self, checked):
        if checked:
            self.checkbox.select()
        else:
            self.checkbox.deselect()
            
    def get_checked(self):
        return self.checkbox_var.get()


class ModernConfigPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        
        self.current_service = None
        self.config_vars = {}
        self.configs = {}
        
        from ..core.connection_tester import ConnectionTester
        from ..collectors.manager import CollectorManager
        self.tester = ConnectionTester()
        self.collector_manager = CollectorManager()
        
        # Load saved configurations
        self.load_saved_configs()
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Service Configuration",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        self.service_label = ctk.CTkLabel(
            self,
            text="Select a service to configure",
            font=("Arial", 14)
        )
        self.service_label.pack(pady=(0, 15))
        
        # Config container
        self.config_container = ctk.CTkFrame(self, fg_color="transparent")
        self.config_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=(5, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", padx=20, pady=(10, 20))
        
        self.test_btn = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            width=120,
            state="disabled",
            command=self.test_connection
        )
        self.test_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="Save Configuration",
            width=140,
            state="disabled",
            command=self.save_config
        )
        self.save_btn.pack(side="left", padx=5)
        
    def show_service_config(self, service_name, host_info=None):
        """Show configuration for a specific service"""
        self.current_service = service_name
        self.service_label.configure(text=f"Configure: {service_name}")
        self.test_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.status_label.configure(text="")
        
        # Clear current config
        for widget in self.config_container.winfo_children():
            widget.destroy()
        self.config_vars.clear()
        
        # Get service requirements
        requirements = self.get_service_requirements(service_name)
        
        # Create input fields
        for req in requirements:
            frame = ctk.CTkFrame(self.config_container, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            label_widget = ctk.CTkLabel(frame, text=f"{req['label']}:", width=100, anchor="w")
            label_widget.pack(side="left")
            
            var = tk.StringVar()
            self.config_vars[req['key']] = var
            
            # Pre-fill values
            if host_info and req['key'] == 'host':
                var.set(host_info['host'])
            elif host_info and req['key'] == 'port' and host_info.get('ports'):
                var.set(str(host_info['ports'][0]))
            
            if req['type'] == 'password':
                entry = ctk.CTkEntry(frame, textvariable=var, show="*", width=250)
            else:
                entry = ctk.CTkEntry(frame, textvariable=var, width=250)
            entry.pack(side="left", padx=(10, 0))
            
    def get_service_requirements(self, service_name):
        """Get configuration requirements for a service"""
        service_reqs = {
            "Plex": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text"},
                {"key": "token", "label": "Token", "type": "password"},
            ],
            "Radarr": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text"},
                {"key": "api_key", "label": "API Key", "type": "password"},
            ],
            "Sonarr": [
                {"key": "host", "label": "Host/IP", "type": "text"},
                {"key": "port", "label": "Port", "type": "text"},
                {"key": "api_key", "label": "API Key", "type": "password"},
            ],
        }
        
        default = [
            {"key": "host", "label": "Host/IP", "type": "text"},
            {"key": "port", "label": "Port", "type": "text"},
        ]
        
        return service_reqs.get(service_name, default)
        
    def test_connection(self):
        """Test the connection"""
        if not self.current_service:
            return
            
        config = {}
        for key, var in self.config_vars.items():
            value = var.get()
            if value:
                config[key] = value
                
        self.status_label.configure(text="Testing connection...", text_color="orange")
        self.update()
        
        success, message = self.tester.test_connection(self.current_service, config)
        
        if success:
            self.status_label.configure(text=f"✓ {message}", text_color="green")
        else:
            self.status_label.configure(text=f"✗ {message}", text_color="red")
            
    def save_config(self):
        """Save configuration"""
        self.status_label.configure(text="✓ Configuration saved!", text_color="green")
    
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
            self.saved_configs = {}
