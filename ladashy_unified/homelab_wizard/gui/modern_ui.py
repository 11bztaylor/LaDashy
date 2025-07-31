"""
Modern UI components using customtkinter
"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernServiceCard(ctk.CTkFrame):
    def __init__(self, parent, service_name, icon_name, on_click, on_toggle, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        
        self.service_name = service_name
        self.on_click = on_click
        self.on_toggle = on_toggle
        self.is_selected = False
        self.is_connected = False
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Checkbox
        self.checkbox = ctk.CTkCheckBox(
            self, 
            text="",
            width=24,
            command=self._on_checkbox_toggle
        )
        self.checkbox.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Icon placeholder (you can add real icons here)
        self.icon_label = ctk.CTkLabel(
            self,
            text=self._get_icon_emoji(icon_name),
            font=("Arial", 20),
            width=30
        )
        self.icon_label.grid(row=0, column=1, padx=(5, 10), sticky="w")
        
        # Service name
        self.name_label = ctk.CTkLabel(
            self,
            text=service_name,
            font=("Arial", 14),
            anchor="w",
            cursor="hand2"
        )
        self.name_label.grid(row=0, column=2, padx=(0, 10), sticky="ew")
        self.name_label.bind("<Button-1>", lambda e: self._on_name_click())
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 16),
            width=30
        )
        self.status_label.grid(row=0, column=3, padx=(5, 10))
        
        # Configure hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _get_icon_emoji(self, icon_name):
        """Get emoji icon for service"""
        icons = {
            "plex": "🎬",
            "jellyfin": "🎭",
            "emby": "📺",
            "radarr": "🎦",
            "sonarr": "📺",
            "prowlarr": "🔍",
            "nginx": "🌐",
            "pihole": "🛡️",
            "portainer": "🐳",
            "prometheus": "📊",
            "default": "📦"
        }
        return icons.get(icon_name, icons["default"])
        
    def _on_enter(self, event):
        if not self.is_selected:
            self.configure(fg_color=("gray85", "gray25"))
            
    def _on_leave(self, event):
        if not self.is_selected:
            self.configure(fg_color=("gray92", "gray14"))
            
    def _on_checkbox_toggle(self):
        self.on_toggle(self.service_name)
        
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
            self.is_connected = True
        elif status == 'error':
            self.status_label.configure(text="✗", text_color="red")
            self.is_connected = False
        elif status == 'configured':
            self.status_label.configure(text="●", text_color="orange")
        else:
            self.status_label.configure(text="")
            
    def set_checked(self, checked):
        if checked:
            self.checkbox.select()
        else:
            self.checkbox.deselect()


class ModernServiceList(ctk.CTkScrollableFrame):
    def __init__(self, parent, service_vars, on_service_click, on_service_toggle, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.service_vars = service_vars
        self.on_service_click = on_service_click
        self.on_service_toggle = on_service_toggle
        self.service_cards = {}
        self.category_frames = {}
        
    def add_category(self, category_name, services):
        """Add a category with services"""
        # Category header
        category_frame = ctk.CTkFrame(self, corner_radius=8)
        category_frame.pack(fill="x", padx=5, pady=(10, 5))
        
        # Category title with arrow
        self.expanded = tk.BooleanVar(value=True)
        header_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        arrow_label = ctk.CTkLabel(
            header_frame,
            text="▼",
            font=("Arial", 12),
            cursor="hand2"
        )
        arrow_label.pack(side="left", padx=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=category_name,
            font=("Arial", 16, "bold")
        )
        title_label.pack(side="left")
        
        # Services container
        services_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        services_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Add service cards
        for service in services:
            card = ModernServiceCard(
                services_frame,
                service["name"],
                service.get("icon", "default"),
                self.on_service_click,
                self.on_service_toggle,
                height=50
            )
            card.pack(fill="x", padx=5, pady=2)
            self.service_cards[service["name"]] = card
            
            # Set initial checkbox state
            if service["name"] in self.service_vars:
                if self.service_vars[service["name"]].get():
                    card.set_checked(True)
        
        # Toggle functionality
        def toggle_category():
            if services_frame.winfo_viewable():
                services_frame.pack_forget()
                arrow_label.configure(text="▶")
            else:
                services_frame.pack(fill="x", padx=5, pady=(0, 5))
                arrow_label.configure(text="▼")
                
        arrow_label.bind("<Button-1>", lambda e: toggle_category())
        title_label.bind("<Button-1>", lambda e: toggle_category())
        
        self.category_frames[category_name] = services_frame
        
    def update_service_status(self, service_name, status):
        """Update service status"""
        if service_name in self.service_cards:
            self.service_cards[service_name].set_status(status)
            
    def highlight_service(self, service_name):
        """Highlight selected service"""
        for name, card in self.service_cards.items():
            card.set_selected(name == service_name)


class ModernConfigPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        
        self.current_service = None
        self.config_vars = {}
        self.configs = {}
        
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
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", fill="x", padx=20, pady=(10, 20))
        
        self.test_btn = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            width=120,
            state="disabled"
        )
        self.test_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="Save Configuration",
            width=140,
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(side="left", padx=(20, 0))
        
    def show_service_config(self, service_name, host_info=None):
        """Show configuration for a specific service"""
        self.current_service = service_name
        self.service_label.configure(text=f"Configure: {service_name}")
        self.test_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        
        # Clear current config
        for widget in self.config_container.winfo_children():
            widget.destroy()
        self.config_vars.clear()
        
        # Example fields
        fields = [
            ("Host/IP", "host", host_info.get('host', '') if host_info else ''),
            ("Port", "port", str(host_info['ports'][0]) if host_info and host_info.get('ports') else ''),
            ("API Key", "api_key", ''),
        ]
        
        for label, key, default in fields:
            frame = ctk.CTkFrame(self.config_container, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            label_widget = ctk.CTkLabel(frame, text=f"{label}:", width=100, anchor="w")
            label_widget.pack(side="left")
            
            var = tk.StringVar(value=default)
            self.config_vars[key] = var
            
            if "password" in key.lower() or "token" in key.lower() or "api" in key.lower():
                entry = ctk.CTkEntry(frame, textvariable=var, show="*", width=250)
            else:
                entry = ctk.CTkEntry(frame, textvariable=var, width=250)
            entry.pack(side="left", padx=(10, 0))
