"""
Main GUI window for the wizard
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ..services.definitions import SERVICES
from ..services.icons import get_icon
from ..core.scanner import NetworkScanner
from .network_config import NetworkConfigDialog
from .enhanced_service_list import EnhancedServiceList
from .config_panel import ServiceConfigPanel
from .scan_dialog import ScanProgressDialog

class HomelabWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏠 Homelab Documentation Wizard")
        self.root.configure(bg='#1e1e1e')
        self.root.geometry("1000x700")
        
        # Storage
        self.service_vars = {}
        self.scanner = NetworkScanner()
        self.discovered_services = {}
        
        # Build GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Build the GUI"""
        # Header
        self.create_header()
        
        # Content
        self.create_content()
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame, 
            text="🏠 Homelab Documentation Wizard",
            font=('Arial', 24, 'bold'), 
            bg='#2d2d2d', 
            fg='white'
        )
        title.pack(pady=20)
        
    
    def create_content(self):
        """Create main content area"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add tabs
        self.create_welcome_tab()
        self.create_services_tab()
        self.create_discovered_tab()
        
    def create_welcome_tab(self):
        """Create welcome tab"""
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        welcome_text = """Welcome to the Homelab Documentation Wizard!
        
This tool will help you document your self-hosted services.

Current networks configured for scanning:"""
        
        ttk.Label(welcome_frame, text=welcome_text, 
                 font=('Arial', 12)).pack(pady=20)
        
        # Show configured networks
        self.network_list_label = ttk.Label(welcome_frame, text="", font=('Arial', 10))
        self.network_list_label.pack()
        self.update_network_list()
        
        # Network config button
        ttk.Button(welcome_frame, text="Configure Networks", 
                  command=self.configure_networks).pack(pady=20)
                 
    def create_services_tab(self):
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
        self.create_service_list(left_panel)
    def create_discovered_tab(self):
        """Create discovered services tab"""
        discovered_frame = ttk.Frame(self.notebook)
        self.notebook.add(discovered_frame, text="Discovered")
        
        # Instructions
        ttk.Label(discovered_frame, text="Services discovered on your network:",
                 font=('Arial', 12)).pack(pady=10)
        
        # Discovered services tree
        tree_frame = ttk.Frame(discovered_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview
        self.discovered_tree = ttk.Treeview(tree_frame, columns=('Service', 'Ports'), 
                                          show='tree headings')
        self.discovered_tree.heading('Service', text='Service')
        self.discovered_tree.heading('Ports', text='Ports')
        
        self.discovered_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', 
                                 command=self.discovered_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.discovered_tree.configure(yscrollcommand=scrollbar.set)
        
    def create_service_list(self, parent):
        """Create the modern service selection list"""
        from ..services.definitions import SERVICES
        
        # Initialize service_vars first
        for category, services in SERVICES.items():
            for service in services:
                if service["name"] not in self.service_vars:
                    self.service_vars[service["name"]] = tk.BooleanVar()
        
        # Create modern service list
        self.service_list = EnhancedServiceList(
            parent, 
            self.service_vars,
            self.on_service_click,
            self.on_service_toggle
        )
        
        # Add all categories and services
        for category, services in SERVICES.items():
            self.service_list.add_category(category, services)
    def create_footer(self):
        """Create footer with buttons"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill='x', padx=10, pady=10)
        
        # Status label
        self.status_label = ttk.Label(footer_frame, text="Ready")
        self.status_label.pack(side='left')
        
        # Generate button
        generate_btn = ttk.Button(footer_frame, text="🚀 Generate Documentation",
                                 command=self.generate_docs)
        generate_btn.pack(side='right')
        
    def update_network_list(self):
        """Update the network list display"""
        networks = self.scanner.get_networks()
        if networks:
            network_text = "\n".join(f"  • {net}" for net in networks)
        else:
            network_text = "  No networks configured"
        self.network_list_label.config(text=network_text)
        
    def configure_networks(self):
        """Open network configuration dialog"""
        dialog = NetworkConfigDialog(self.root, self.scanner)
        self.root.wait_window(dialog.dialog)
        
        # Update display
        self.update_network_list()
        
    def scan_network(self):
        """Scan network for services"""
        if not self.scanner.get_networks():
            messagebox.showwarning("No Networks", 
                                 "Please configure networks to scan first")
            self.configure_networks()
            return
            
        # Show scan dialog
        scan_dialog = ScanProgressDialog(self.root, self.scanner)
        self.root.wait_window(scan_dialog.dialog)
        
        # Get results
        self.discovered_services = scan_dialog.get_results()
        
        # Update UI with results
        self.update_discovered_services()
        
    def update_discovered_services(self):
        """Update UI with discovered services"""
        # Clear tree
        for item in self.discovered_tree.get_children():
            self.discovered_tree.delete(item)
        
        # Add discovered services
        for ip, host_info in self.discovered_services.items():
            # Add host
            host_item = self.discovered_tree.insert('', 'end', 
                                                   text=f"{ip} ({host_info['hostname']})")
            
            # Add services
            for service in host_info['services']:
                ports = ', '.join(map(str, service['ports']))
                self.discovered_tree.insert(host_item, 'end', 
                                          values=(service['name'], ports))
                
                # Auto-check the service
                if service['name'] in self.service_vars:
                    self.service_vars[service['name']].set(True)
                    # Show config panel for first service
                    if not hasattr(self, '_first_service_shown'):
                        self._first_service_shown = True
                        host_info = {
                            'host': ip,
                            'ports': service.get('ports', []),
                            'hostname': info.get('hostname', 'Unknown')
                        }
                        self.config_panel.show_service_config(service['name'], host_info)
        
        # Switch to discovered tab
        self.notebook.select(2)
        
        # Update status
        total_services = sum(len(h['services']) for h in self.discovered_services.values())
        self.status_label.config(text=f"Found {total_services} services")
        
    
    def on_service_toggle(self, service_name):
        """Handle service checkbox toggle"""
        # Always show config panel when toggled
        self.show_service_config(service_name)
        
    def on_service_click(self, service_name):
        """Handle clicking on service name"""
        # Show config panel without changing checkbox
        self.show_service_config(service_name)
        
    def show_service_config(self, service_name):
        """Show configuration for a service"""
        # Highlight the service
        self.service_list.highlight_service(service_name)
        
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
    def select_all(self):
        """Select all services"""
        for var in self.service_vars.values():
            var.set(True)
            
    def clear_all(self):
        """Clear all services"""
        for var in self.service_vars.values():
            var.set(False)
        
    
    def update_service_status(self, service_name, status):
        """Update visual status of a service"""
        if hasattr(self, 'service_list'):
            self.service_list.update_service_status(service_name, status)

    def generate_docs(self):
        """Generate documentation"""
        selected = [name for name, var in self.service_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select services to document")
            return
            
        # Show what will be documented
        msg = f"Will generate documentation for {len(selected)} services:\n\n"
        msg += "\n".join(f"• {s}" for s in selected[:10])
        if len(selected) > 10:
            msg += f"\n... and {len(selected) - 10} more"
            
        messagebox.showinfo("Generating Documentation", msg)
        
    def run(self):
        """Run the application"""
        self.root.mainloop()
