"""
Network configuration dialog - simplified version
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress

class NetworkConfigDialog:
    def __init__(self, parent, scanner):
        self.scanner = scanner
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Network Configuration")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        # Instructions
        instructions = ttk.Label(
            self.dialog,
            text="Configure networks to scan for services:",
            font=('Arial', 10)
        )
        instructions.pack(pady=10)
        
        # Current networks frame
        list_frame = ttk.LabelFrame(self.dialog, text="Networks to Scan", padding=15)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Listbox for networks
        self.network_listbox = tk.Listbox(list_frame, height=8)
        self.network_listbox.pack(fill='both', expand=True)
        
        # Populate with current networks
        for network in self.scanner.get_networks():
            self.network_listbox.insert(tk.END, network)
        
        # Remove button
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Remove Selected", 
                  command=self.remove_network).pack(side='right')
        
        # Add network frame
        add_frame = ttk.LabelFrame(self.dialog, text="Add Network", padding=15)
        add_frame.pack(fill='x', padx=20, pady=10)
        
        # Network input with separate IP and CIDR
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill='x')
        
        ttk.Label(input_frame, text="Network:").pack(side='left', padx=(0, 10))
        
        # IP address entry
        self.network_entry = ttk.Entry(input_frame, width=15)
        self.network_entry.pack(side='left')
        self.network_entry.insert(0, "192.168.1.0")
        
        ttk.Label(input_frame, text="/").pack(side='left', padx=5)
        
        # CIDR dropdown
        self.cidr_var = tk.StringVar(value="24")
        self.cidr_dropdown = ttk.Combobox(
            input_frame, 
            textvariable=self.cidr_var,
            values=[str(i) for i in range(32, 7, -1)],  # 32 down to 8
            width=4,
            state='readonly'
        )
        self.cidr_dropdown.pack(side='left')
        
        ttk.Button(input_frame, text="Add", 
                  command=self.add_network).pack(side='left', padx=20)
        
        # Tips
        tips_text = "Common networks: 192.168.1.0/24, 192.168.0.0/24, 10.0.0.0/24"
        ttk.Label(add_frame, text=tips_text, font=('Arial', 9), 
                 foreground='gray').pack(pady=(10, 0))
        
        # Dialog buttons
        dialog_buttons = ttk.Frame(self.dialog)
        dialog_buttons.pack(fill='x', pady=15)
        
        ttk.Button(dialog_buttons, text="Close", 
                  command=self.dialog.destroy).pack(side='right', padx=20)
        
    def add_network(self):
        """Add a network to the scan list"""
        ip_part = self.network_entry.get().strip()
        cidr_part = self.cidr_var.get()
        
        if not ip_part:
            messagebox.showwarning("Input Required", "Please enter a network address")
            return
        
        # Combine IP and CIDR
        network = f"{ip_part}/{cidr_part}"
        
        # Validate and add
        try:
            # Validate the network format
            ipaddress.ip_network(network)
            
            # Check if already exists
            items = self.network_listbox.get(0, tk.END)
            if network in items:
                messagebox.showinfo("Already Added", f"{network} is already in the list")
                return
            
            # Add to scanner and list
            if self.scanner.add_network(network):
                self.network_listbox.insert(tk.END, network)
                # Reset to default
                self.network_entry.delete(0, tk.END)
                self.network_entry.insert(0, "192.168.1.0")
            else:
                messagebox.showerror("Error", f"Failed to add network: {network}")
                
        except ValueError as e:
            messagebox.showerror("Invalid Network", 
                               f"Invalid network address: {network}\n\n"
                               f"Error: {str(e)}")
    
    def remove_network(self):
        """Remove selected network"""
        selection = self.network_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a network to remove")
            return
        
        network = self.network_listbox.get(selection[0])
        
        # Confirm if it's the last network
        if self.network_listbox.size() == 1:
            if not messagebox.askyesno("Confirm", 
                                     "This is the last network. Remove it anyway?"):
                return
        
        self.scanner.remove_network(network)
        self.network_listbox.delete(selection[0])
