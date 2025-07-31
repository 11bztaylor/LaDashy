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
from .scan_dialog import ScanProgressDialog

class HomelabWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏠 Homelab Documentation Wizard")
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
        header_frame = tk.Frame(self.root, bg='#1e1e1e', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🏠 Homelab Documentation Wizard",
                        font=('Arial', 24, 'bold'), bg='#1e1e1e', fg='white')
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
        """Create services selection tab"""
        services_frame = ttk.Frame(self.notebook)
        self.notebook.add(services_frame, text="Services")
        
        # Control buttons
        control_frame = ttk.Frame(services_frame)
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
        self.create_service_list(services_frame)
        
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
        """Create the service selection list"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add services
        for category, services in SERVICES.items():
            # Category frame
            cat_frame = ttk.LabelFrame(scrollable_frame, text=category, padding=10)
            cat_frame.pack(fill='x', padx=10, pady=5)
            
            # Add services
            for service in services:
                var = tk.BooleanVar()
                self.service_vars[service["name"]] = var
                
                cb = ttk.Checkbutton(cat_frame, text=service["name"], variable=var)
                cb.pack(anchor='w', pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
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
        
        # Switch to discovered tab
        self.notebook.select(2)
        
        # Update status
        total_services = sum(len(h['services']) for h in self.discovered_services.values())
        self.status_label.config(text=f"Found {total_services} services")
        
    def select_all(self):
        """Select all services"""
        for var in self.service_vars.values():
            var.set(True)
            
    def clear_all(self):
        """Clear all services"""
        for var in self.service_vars.values():
            var.set(False)
        
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
