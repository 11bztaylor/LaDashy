"""
Modern main window using customtkinter
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from .modern_ui_fixed import ModernServiceCard, ModernConfigPanel
import customtkinter as ctk
from ..core.scanner import NetworkScanner
from ..services.definitions import SERVICES
from .scan_dialog import ScanProgressDialog
from .network_config import NetworkConfigDialog

class ModernHomelabWizard:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🏠 Homelab Documentation Wizard")
        self.root.geometry("1200x700")
        
        # Storage
        self.service_vars = {}
        self.scanner = NetworkScanner()
        self.discovered_services = {}
        
        # Initialize service vars
        for category, services in SERVICES.items():
            for service in services:
                self.service_vars[service["name"]] = tk.BooleanVar()
        
        # Build GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Build the modern GUI"""
        # Configure grid
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="🏠 Homelab Documentation Wizard",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=20)
        
        # Left panel - Services
        left_panel = ctk.CTkFrame(self.root)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Control buttons
        control_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        scan_btn = ctk.CTkButton(
            control_frame,
            text="🔍 Scan Network",
            command=self.scan_network,
            width=140
        )
        scan_btn.pack(side="left", padx=5)
        
        config_btn = ctk.CTkButton(
            control_frame,
            text="⚙️ Configure Networks",
            command=self.configure_networks,
            width=140
        )
        config_btn.pack(side="left", padx=5)
        
        
        # Service list frame
        service_frame = ctk.CTkFrame(left_panel)
        service_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Service list label
        list_label = ctk.CTkLabel(service_frame, text="Services", font=("Arial", 16, "bold"))
        list_label.pack(pady=(10, 5))
        
        # Scrollable frame for services
        self.service_scroll = ctk.CTkScrollableFrame(service_frame)
        self.service_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.service_cards = {}
        
        # Add all services
        for category, services in SERVICES.items():
            # Category header
            cat_label = ctk.CTkLabel(
                self.service_scroll,
                text=category,
                font=("Arial", 14, "bold"),
                anchor="w"
            )
            cat_label.pack(fill="x", padx=10, pady=(10, 5))
            
            # Service cards
            for service in services:
                card = ModernServiceCard(
                    self.service_scroll,
                    service["name"],
                    service.get("icon", "default"),
                    self.on_service_click,
                    self.on_service_toggle
                )
                card.pack(fill="x", padx=5, pady=2)
                self.service_cards[service["name"]] = card

        # Right panel - Configuration
        self.config_panel = ModernConfigPanel(self.root)
        self.config_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Bottom status bar
        status_frame = ctk.CTkFrame(self.root, height=40, corner_radius=0)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        status_frame.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready")
        self.status_label.pack(side="left", padx=20, pady=10)
        
        generate_btn = ctk.CTkButton(
            status_frame,
            text="🚀 Generate Documentation",
            command=self.generate_docs,
            width=180,
            height=30
        )
        generate_btn.pack(side="right", padx=20, pady=5)
        
    def on_service_click(self, service_name):
        """Handle service name click"""
        # Highlight the selected card
        for name, card in self.service_cards.items():
            card.set_selected(name == service_name)
        
        # Find host info if discovered
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
                    
        self.config_panel.show_service_config(service_name, host_info)
        
    
    def on_service_toggle(self, service_name, checked):
        """Handle service checkbox toggle"""
        self.service_vars[service_name].set(checked)
        if checked:
            self.on_service_click(service_name)

    
    def scan_network(self):
        """Scan network for services"""
        if not self.scanner.get_networks():
            messagebox.showwarning("No Networks", "Please configure networks to scan first")
            self.configure_networks()
            return
            
        # Show scan dialog
        scan_dialog = ScanProgressDialog(self.root, self.scanner)
        self.root.wait_window(scan_dialog.dialog)
        
        # Get results
        self.discovered_services = scan_dialog.get_results()
        
        # Update UI
        self.update_discovered_services()
        
    def update_discovered_services(self):
        """Update UI with discovered services"""
        for ip, info in self.discovered_services.items():
            for service in info.get('services', []):
                service_name = service['name']
                
                # Auto-check discovered services
                if service_name in self.service_vars:
                    self.service_vars[service_name].set(True)
                    self.service_list.service_cards[service_name].set_checked(True)
                    
                    # Update status based on confidence
                    confidence = service.get('confidence', 1.0)
                    if confidence > 0.8:
                        self.service_list.update_service_status(service_name, 'configured')
                        
        # Update status
        total_services = sum(len(h.get('services', [])) for h in self.discovered_services.values())
        self.status_label.configure(text=f"Found {total_services} services")
        
    def configure_networks(self):
        """Open network configuration dialog"""
        dialog = NetworkConfigDialog(self.root, self.scanner)
        self.root.wait_for_visibility()  # Ensure window is visible before grab
        self.root.wait_window(dialog.dialog)
        
    def generate_docs(self):
        """Generate documentation"""
        selected = [name for name, var in self.service_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select services to document")
            return
            
        messagebox.showinfo("Generating Documentation", f"Will generate docs for {len(selected)} services")
        
    def mark_configured_services(self, service_names):
        """Mark services as configured"""
        for service_name in service_names:
            if service_name in self.service_cards:
                self.service_cards[service_name].set_status('configured')
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
