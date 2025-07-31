"""
Service information display panel
"""
import tkinter as tk
from tkinter import ttk
import threading
import json

class ServiceInfoPanel:
    def __init__(self, parent, bg_color='#2d2d2d'):
        self.parent = parent
        self.bg_color = bg_color
        self.current_service = None
        self.current_config = None
        self.info_labels = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the info panel UI"""
        # Main frame
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        
        # Title
        self.title_label = tk.Label(
            self.frame,
            text="Service Information",
            font=('Arial', 14, 'bold'),
            bg=self.bg_color,
            fg='white'
        )
        self.title_label.pack(pady=(10, 15))
        
        # Info container
        self.info_container = tk.Frame(self.frame, bg=self.bg_color)
        self.info_container.pack(fill='both', expand=True, padx=20)
        
        # Status message
        self.status_label = tk.Label(
            self.frame,
            text="Connect to a service to see information",
            font=('Arial', 10),
            bg=self.bg_color,
            fg='#888888'
        )
        self.status_label.pack(pady=10)
        
    def show_service_info(self, service_name, config, collector_manager):
        """Display information for connected service"""
        self.current_service = service_name
        self.current_config = config
        
        # Clear previous info
        for widget in self.info_container.winfo_children():
            widget.destroy()
        self.info_labels.clear()
        
        # Update status
        self.status_label.config(text="Loading service information...", fg='#ffaa00')
        
        # Start background thread to collect data
        thread = threading.Thread(
            target=self._collect_and_display,
            args=(service_name, config, collector_manager)
        )
        thread.daemon = True
        thread.start()
        
    def _collect_and_display(self, service_name, config, collector_manager):
        """Collect and display service data"""
        try:
            # Collect data
            data = collector_manager.collect_service_data(service_name, config)
            
            if data.get('status') == 'success':
                # Update UI in main thread
                self.parent.after(0, self._update_display, service_name, data)
            else:
                self.parent.after(0, self._show_error, data.get('error', 'Unknown error'))
                
        except Exception as e:
            self.parent.after(0, self._show_error, str(e))
            
    def _update_display(self, service_name, data):
        """Update the display with collected data"""
        basic = data.get('basic', {})
        detailed = data.get('detailed', {})
        
        # Clear container
        for widget in self.info_container.winfo_children():
            widget.destroy()
            
        # Service-specific displays
        if service_name == "Plex":
            self._display_plex_info(basic, detailed)
        elif service_name == "Radarr":
            self._display_radarr_info(basic, detailed)
        elif service_name == "Sonarr":
            self._display_sonarr_info(basic, detailed)
        else:
            self._display_generic_info(basic, detailed)
            
        self.status_label.config(text="✓ Information loaded", fg='#4caf50')
        
    def _display_plex_info(self, basic, detailed):
        """Display Plex-specific information"""
        # Version info
        if basic.get('version'):
            self._add_info_row("Version:", basic['version'])
        if basic.get('platform'):
            self._add_info_row("Platform:", basic['platform'])
            
        # Separator
        ttk.Separator(self.info_container, orient='horizontal').pack(fill='x', pady=10)
        
        # Libraries
        if detailed.get('libraries'):
            lib_frame = tk.Frame(self.info_container, bg=self.bg_color)
            lib_frame.pack(fill='x', pady=5)
            
            tk.Label(
                lib_frame,
                text="Libraries:",
                font=('Arial', 11, 'bold'),
                bg=self.bg_color,
                fg='white'
            ).pack(anchor='w')
            
            for lib in detailed['libraries']:
                lib_text = f"  • {lib['title']} ({lib['type']}): {lib.get('item_count', 0)} items"
                tk.Label(
                    lib_frame,
                    text=lib_text,
                    font=('Arial', 10),
                    bg=self.bg_color,
                    fg='#cccccc'
                ).pack(anchor='w', padx=(20, 0))
                
        # Active sessions
        if 'active_sessions' in detailed:
            self._add_info_row("Active Streams:", str(detailed['active_sessions']))
            
    def _display_radarr_info(self, basic, detailed):
        """Display Radarr-specific information"""
        # Version
        if basic.get('version'):
            self._add_info_row("Version:", basic['version'])
            
        # Movie stats
        if 'total_movies' in detailed:
            self._add_info_row("Total Movies:", str(detailed['total_movies']))
        if 'monitored_movies' in detailed:
            self._add_info_row("Monitored:", str(detailed['monitored_movies']))
        if 'downloaded_movies' in detailed:
            self._add_info_row("Downloaded:", str(detailed['downloaded_movies']))
            
        # Queue
        if 'queue_count' in detailed:
            self._add_info_row("In Queue:", str(detailed['queue_count']))
            
        # Storage
        if detailed.get('root_folders'):
            ttk.Separator(self.info_container, orient='horizontal').pack(fill='x', pady=10)
            tk.Label(
                self.info_container,
                text="Storage:",
                font=('Arial', 11, 'bold'),
                bg=self.bg_color,
                fg='white'
            ).pack(anchor='w')
            
            for folder in detailed['root_folders']:
                if folder.get('freeSpace') and folder.get('totalSpace'):
                    free_gb = folder['freeSpace'] / (1024**3)
                    total_gb = folder['totalSpace'] / (1024**3)
                    used_pct = ((total_gb - free_gb) / total_gb) * 100
                    
                    folder_text = f"  {folder['path']}: {free_gb:.1f}GB free ({used_pct:.0f}% used)"
                    tk.Label(
                        self.info_container,
                        text=folder_text,
                        font=('Arial', 9),
                        bg=self.bg_color,
                        fg='#cccccc'
                    ).pack(anchor='w', padx=(20, 0))
                    
    def _display_sonarr_info(self, basic, detailed):
        """Display Sonarr-specific information"""
        # Similar to Radarr but for TV shows
        if basic.get('version'):
            self._add_info_row("Version:", basic['version'])
            
        if 'total_series' in detailed:
            self._add_info_row("Total Series:", str(detailed['total_series']))
        if 'monitored_series' in detailed:
            self._add_info_row("Monitored:", str(detailed['monitored_series']))
            
    def _display_generic_info(self, basic, detailed):
        """Display generic service information"""
        # Show all basic info
        for key, value in basic.items():
            if key != 'error':
                label = key.replace('_', ' ').title() + ":"
                self._add_info_row(label, str(value))
                
    def _add_info_row(self, label, value):
        """Add an information row"""
        row_frame = tk.Frame(self.info_container, bg=self.bg_color)
        row_frame.pack(fill='x', pady=2)
        
        tk.Label(
            row_frame,
            text=label,
            font=('Arial', 10, 'bold'),
            bg=self.bg_color,
            fg='white',
            width=15,
            anchor='w'
        ).pack(side='left')
        
        tk.Label(
            row_frame,
            text=value,
            font=('Arial', 10),
            bg=self.bg_color,
            fg='#cccccc',
            anchor='w'
        ).pack(side='left', fill='x', expand=True)
        
    def _show_error(self, error):
        """Show error message"""
        self.status_label.config(text=f"✗ Error: {error}", fg='#f44336')
        
    def get_frame(self):
        """Get the panel frame"""
        return self.frame
        
    def clear_info(self):
        """Clear all displayed information"""
        for widget in self.info_container.winfo_children():
            widget.destroy()
        self.info_labels.clear()
        self.status_label.config(text="Connect to a service to see information", fg='#888888')
