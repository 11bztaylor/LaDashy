"""
Modern service list with collapsible categories and status indicators
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ModernServiceList:
    def __init__(self, parent, service_vars, on_service_click, on_service_toggle):
        self.parent = parent
        self.service_vars = service_vars
        self.on_service_click = on_service_click
        self.on_service_toggle = on_service_toggle
        self.category_frames = {}
        self.service_widgets = {}
        self.service_status = {}  # Track connection status
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the modern service list UI"""
        # Modern color scheme
        self.colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d',
            'bg_hover': '#3d3d3d',
            'bg_selected': '#0d7377',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#14ffec',
            'success': '#4caf50',
            'error': '#f44336',
            'warning': '#ff9800'
        }

        # Modern color scheme
        self.colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d',
            'bg_hover': '#3d3d3d',
            'bg_selected': '#0d7377',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#14ffec',
            'success': '#4caf50',
            'error': '#f44336',
            'warning': '#ff9800'
        }

        # Create scrollable frame
        self.canvas = tk.Canvas(self.parent, bg='#1a1a1a', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
    def add_category(self, category_name, services):
        """Add a collapsible category with services"""
        # Category container
        category_container = tk.Frame(self.scrollable_frame, bg='#2d2d2d', relief='flat')
        category_container.pack(fill='x', padx=5, pady=2)
        
        # Category header
        header_frame = tk.Frame(category_container, bg='#3d3d3d', height=35)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Expand/collapse arrow
        self.expanded = tk.BooleanVar(value=True)
        arrow_label = tk.Label(header_frame, text="▼", font=('Arial', 10), 
                              bg='#e0e0e0', cursor='hand2')
        arrow_label.pack(side='left', padx=(10, 5))
        
        # Category name
        cat_label = tk.Label(header_frame, text=category_name, 
                            font=('Arial', 11, 'bold'), bg='#3d3d3d', fg='#ffffff')
        cat_label.pack(side='left', pady=8)
        
        # Services container
        services_frame = tk.Frame(category_container, bg='white')
        services_frame.pack(fill='x', padx=(20, 0))
        
        # Add services
        for service in services:
            self.add_service(services_frame, service)
        
        # Bind click to toggle
        def toggle_category():
            if services_frame.winfo_viewable():
                services_frame.pack_forget()
                arrow_label.config(text="▶")
            else:
                services_frame.pack(fill='x', padx=(20, 0))
                arrow_label.config(text="▼")
        
        header_frame.bind("<Button-1>", lambda e: toggle_category())
        arrow_label.bind("<Button-1>", lambda e: toggle_category())
        cat_label.bind("<Button-1>", lambda e: toggle_category())
        
        self.category_frames[category_name] = services_frame
        
    def add_service(self, parent, service):
        """Add a modern service item"""
        service_name = service["name"]
        
        # Service container
        service_frame = tk.Frame(parent, bg='#2d2d2d', relief='flat')
        service_frame.pack(fill='x', pady=2)
        
        # Hover effect
        def on_enter(e):
            if service_name in self.service_vars and not self.service_vars[service_name].get():
                service_frame.config(bg='#f5f5f5')
        
        def on_leave(e):
            if service_name in self.service_vars and not self.service_vars[service_name].get():
                service_frame.config(bg='white')
        
        service_frame.bind("<Enter>", on_enter)
        service_frame.bind("<Leave>", on_leave)
        
        # Service content frame
        content_frame = tk.Frame(service_frame, bg='white')
        content_frame.pack(fill='x', padx=10, pady=5)
        
        # Checkbox
        var = self.service_vars[service_name]
        checkbox = tk.Checkbutton(
            content_frame, 
            variable=var,
            bg='white',
            activebackground='white',
            highlightthickness=0,
            command=lambda: self.on_service_toggle(service_name)
        )
        checkbox.pack(side='left', padx=(0, 10))
        
        # Service icon (placeholder for now)
        icon_label = tk.Label(content_frame, text="🔲", font=('Arial', 16), bg='white')
        icon_label.pack(side='left', padx=(0, 10))
        
        # Service name
        name_label = tk.Label(content_frame, text=service_name, 
                             font=('Arial', 10), bg='white', cursor='hand2')
        name_label.pack(side='left')
        
        # Status indicator
        status_label = tk.Label(content_frame, text="", font=('Arial', 12), bg='white')
        status_label.pack(side='right', padx=(10, 0))
        
        # Click handler for name
        def on_name_click(e):
            self.on_service_click(service_name)
        
        name_label.bind("<Button-1>", on_name_click)
        icon_label.bind("<Button-1>", on_name_click)
        
        # Store references
        self.service_widgets[service_name] = {
            'frame': service_frame,
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
            widgets['status_label'].config(text="✓", foreground='green')
            widgets['name_label'].config(foreground='green')
            widgets['frame'].config(bg='#e8f5e9')
        elif status == 'error':
            widgets['status_label'].config(text="✗", foreground='red')
            widgets['name_label'].config(foreground='red')
            widgets['frame'].config(bg='#ffebee')
        elif status == 'configured':
            widgets['status_label'].config(text="●", foreground='orange')
            widgets['name_label'].config(foreground='black')
            widgets['frame'].config(bg='#fff3e0')
        else:
            widgets['status_label'].config(text="")
            widgets['name_label'].config(foreground='black')
            widgets['frame'].config(bg='white')
            
    def highlight_service(self, service_name):
        """Highlight selected service"""
        # Reset all backgrounds
        for name, widgets in self.service_widgets.items():
            if name != service_name:
                status = self.service_status.get(name, 'none')
                if status == 'connected':
                    widgets['frame'].config(bg='#e8f5e9')
                elif status == 'error':
                    widgets['frame'].config(bg='#ffebee')
                elif status == 'configured':
                    widgets['frame'].config(bg='#fff3e0')
                else:
                    widgets['frame'].config(bg='white')
        
        # Highlight selected
        if service_name in self.service_widgets:
            self.service_widgets[service_name]['frame'].config(bg='#e3f2fd')
