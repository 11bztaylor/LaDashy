import os
from PIL import Image, ImageTk
"""
Enhanced service list with better styling for tkinter
"""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

class EnhancedServiceList:
    def __init__(self, parent, service_vars, on_service_click, on_service_toggle):
        self.parent = parent
        self.service_vars = service_vars
        self.on_service_click = on_service_click
        self.on_service_toggle = on_service_toggle
        self.category_frames = {}
        self.service_widgets = {}
        self.service_status = {}
        
        # Modern color scheme
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#2d2d2d',
            'bg_light': '#3a3a3a',
            'bg_hover': '#454545',
            'bg_selected': '#0e4429',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent_green': '#4caf50',
            'accent_red': '#f44336',
            'accent_orange': '#ff9800',
            'accent_blue': '#2196f3'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the enhanced service list UI"""
        # Main container with dark theme
        main_frame = tk.Frame(self.parent, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True)
        
        # Create scrollable frame
        self.canvas = tk.Canvas(main_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_dark'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Style the scrollbar
        style = ttk.Style()
        style.configure("Dark.Vertical.TScrollbar", 
                       background=self.colors['bg_medium'],
                       darkcolor=self.colors['bg_dark'],
                       lightcolor=self.colors['bg_light'],
                       troughcolor=self.colors['bg_dark'],
                       bordercolor=self.colors['bg_dark'])
        
        self.scrollbar.configure(style="Dark.Vertical.TScrollbar")
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
    def add_category(self, category_name, services):
        """Add a collapsible category with services"""
        # Category container with rounded corners effect
        category_container = tk.Frame(self.scrollable_frame, bg=self.colors['bg_medium'])
        category_container.pack(fill='x', padx=10, pady=5)
        
        # Add border effect
        border_frame = tk.Frame(category_container, bg=self.colors['bg_light'], bd=1)
        border_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        inner_frame = tk.Frame(border_frame, bg=self.colors['bg_medium'])
        inner_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Category header
        header_frame = tk.Frame(inner_frame, bg=self.colors['bg_light'], height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Expand/collapse arrow
        self.expanded = tk.BooleanVar(value=True)
        arrow_label = tk.Label(header_frame, text="▼", font=('Arial', 12, 'bold'), 
                              bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                              cursor='hand2')
        arrow_label.pack(side='left', padx=(15, 10))
        
        # Category name
        cat_label = tk.Label(header_frame, text=category_name, 
                            font=('Arial', 12, 'bold'), 
                            bg=self.colors['bg_light'], 
                            fg=self.colors['text_primary'])
        cat_label.pack(side='left', pady=10)
        
        # Services container
        services_frame = tk.Frame(inner_frame, bg=self.colors['bg_medium'])
        services_frame.pack(fill='x', padx=5, pady=5)
        
        # Add services
        for service in services:
            self.add_service(services_frame, service)
        
        # Bind click to toggle
        def toggle_category():
            if services_frame.winfo_viewable():
                services_frame.pack_forget()
                arrow_label.config(text="▶")
            else:
                services_frame.pack(fill='x', padx=5, pady=5)
                arrow_label.config(text="▼")
        
        header_frame.bind("<Button-1>", lambda e: toggle_category())
        arrow_label.bind("<Button-1>", lambda e: toggle_category())
        cat_label.bind("<Button-1>", lambda e: toggle_category())
        
        self.category_frames[category_name] = services_frame
        
    def add_service(self, parent, service):
        """Add an enhanced service item"""
        service_name = service["name"]
        
        # Service container
        service_frame = tk.Frame(parent, bg=self.colors['bg_medium'], relief='flat', height=45)
        service_frame.pack(fill='x', pady=3, padx=5)
        service_frame.pack_propagate(False)
        
        # Inner frame for padding
        inner_frame = tk.Frame(service_frame, bg=self.colors['bg_medium'])
        inner_frame.pack(fill='both', expand=True, padx=10, pady=8)
        
        # Hover effect
        def on_enter(e):
            if service_name not in self.service_status or self.service_status[service_name] != 'selected':
                service_frame.config(bg=self.colors['bg_hover'])
                inner_frame.config(bg=self.colors['bg_hover'])
                for child in inner_frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=self.colors['bg_hover'])
        
        def on_leave(e):
            if service_name not in self.service_status or self.service_status[service_name] != 'selected':
                service_frame.config(bg=self.colors['bg_medium'])
                inner_frame.config(bg=self.colors['bg_medium'])
                for child in inner_frame.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=self.colors['bg_medium'])
        
        service_frame.bind("<Enter>", on_enter)
        service_frame.bind("<Leave>", on_leave)
        for child in [inner_frame]:
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
        
        # Checkbox
        var = self.service_vars[service_name]
        checkbox = tk.Checkbutton(
            inner_frame, 
            variable=var,
            bg=self.colors['bg_medium'],
            activebackground=self.colors['bg_hover'],
            highlightthickness=0,
            bd=0,
            command=lambda: self.on_service_toggle(service_name)
        )
        checkbox.pack(side='left', padx=(0, 10))
        
        # Service icon (image or emoji fallback)
        icon_loaded = False
        safe_name = service_name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        logo_path = f"homelab_wizard/assets/logos/{safe_name}.png"
        
        try:
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                icon_label = tk.Label(inner_frame, image=photo, 
                                     bg=self.colors['bg_medium'])
                icon_label.image = photo  # Keep a reference
                icon_loaded = True
        except:
            pass
            
        if not icon_loaded:
            # Fallback to emoji
            icon_map = {
                'plex': '🎬', 'jellyfin': '🎭', 'emby': '📺',
                'radarr': '🎦', 'sonarr': '📺', 'prowlarr': '🔍',
                'nginx': '🌐', 'pihole': '🛡️', 'portainer': '🐳',
                'default': '📦'
            }
            icon = icon_map.get(service.get('icon', 'default'), '📦')
            icon_label = tk.Label(inner_frame, text=icon, font=('Arial', 16), 
                                 bg=self.colors['bg_medium'], fg=self.colors['text_primary'])
        icon_label.pack(side='left', padx=(0, 10))
        icon_label.bind("<Enter>", on_enter)
        icon_label.bind("<Leave>", on_leave)
        
        # Service name
        name_label = tk.Label(inner_frame, text=service_name, 
                             font=('Arial', 11), bg=self.colors['bg_medium'], 
                             fg=self.colors['text_primary'], cursor='hand2')
        name_label.pack(side='left')
        name_label.bind("<Enter>", on_enter)
        name_label.bind("<Leave>", on_leave)
        
        # Status indicator
        status_label = tk.Label(inner_frame, text="", font=('Arial', 14), 
                               bg=self.colors['bg_medium'])
        status_label.pack(side='right', padx=(10, 0))
        status_label.bind("<Enter>", on_enter)
        status_label.bind("<Leave>", on_leave)
        
        # Click handler for name
        def on_name_click(e):
            self.on_service_click(service_name)
            self.highlight_service(service_name)
        
        name_label.bind("<Button-1>", on_name_click)
        icon_label.bind("<Button-1>", on_name_click)
        
        # Store references
        self.service_widgets[service_name] = {
            'frame': service_frame,
            'inner_frame': inner_frame,
            'checkbox': checkbox,
            'name_label': name_label,
            'status_label': status_label,
            'icon_label': icon_label
        }
        
    def update_service_status(self, service_name, status):
        """Update service connection status"""
        if service_name not in self.service_widgets:
            return
            
        widgets = self.service_widgets[service_name]
        self.service_status[service_name] = status
        
        if status == 'connected':
            widgets['status_label'].config(text="✓", fg=self.colors['accent_green'])
            widgets['name_label'].config(fg=self.colors['accent_green'])
        elif status == 'error':
            widgets['status_label'].config(text="✗", fg=self.colors['accent_red'])
            widgets['name_label'].config(fg=self.colors['accent_red'])
        elif status == 'configured':
            widgets['status_label'].config(text="●", fg=self.colors['accent_orange'])
            widgets['name_label'].config(fg=self.colors['text_primary'])
        else:
            widgets['status_label'].config(text="")
            widgets['name_label'].config(fg=self.colors['text_primary'])
            
    def highlight_service(self, service_name):
        """Highlight selected service"""
        # Reset all backgrounds
        for name, widgets in self.service_widgets.items():
            if name == service_name:
                widgets['frame'].config(bg=self.colors['bg_selected'])
                widgets['inner_frame'].config(bg=self.colors['bg_selected'])
                for child in widgets['inner_frame'].winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=self.colors['bg_selected'])
                self.service_status[name] = 'selected'
            else:
                widgets['frame'].config(bg=self.colors['bg_medium'])
                widgets['inner_frame'].config(bg=self.colors['bg_medium'])
                for child in widgets['inner_frame'].winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=self.colors['bg_medium'])
                if name in self.service_status and self.service_status[name] == 'selected':
                    del self.service_status[name]
