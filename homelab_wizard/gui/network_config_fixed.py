"""
Network configuration dialog - improved version
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress

class NetworkConfigDialog:
    def __init__(self, parent, scanner):
        self.scanner = scanner
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Network Configuration")
        self.dialog.geometry("550x500")  # Made taller
        self.dialog.resizable(False, False)  # Prevent resizing
        
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
        list_frame = ttk.LabelFrame(self.dialog, text="Networks to Scan", padding=10)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Listbox for networks
        self.network_listbox = tk.Listbox(list_frame, height=8)
        self.network_listbox.pack(fill='both', expand=True)
        
        # Populate with current networks
        for network in self.scanner.get_networks():
            self.network_listbox.insert(tk.END, network)
        
        # Remove button
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Remove Selected", 
                  command=self.remove_network).pack(side='right')
        
        # Add network frame
        add_frame = ttk.LabelFrame(self.dialog, text="Add Network", padding=10)
        add_frame.pack(fill='x', padx=20, pady=10)
        
        # Network input with separate IP and CIDR
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_frame, text="Network:").pack(side='left')
        
        # IP address entry
        self.network_entry = ttk.Entry(input_frame, width=15)
        self.network_entry.pack(side='left', padx=5)
        self.network_entry.insert(0, "192.168.1.0")
        
        ttk.Label(input_frame, text="/").pack(side='left')
        
        # CIDR dropdown
        self.cidr_var = tk.StringVar(value="24")
        self.cidr_dropdown = ttk.Combobox(
            input_frame, 
            textvariable=self.cidr_var,
            values=[str(i) for i in range(32, 7, -1)],  # 32 down to 8
            width=3,
            state='readonly'
        )
        self.cidr_dropdown.pack(side='left', padx=5)
        
        ttk.Button(input_frame, text="Add", 
                  command=self.add_network).pack(side='left', padx=10)
        
        # Common networks section
        common_frame = ttk.LabelFrame(add_frame, text="Quick Add Common Networks", padding=10)
        common_frame.pack(fill='x', pady=10)
        
        # Create two columns for common networks
        common_networks = [
            ("192.168.1.0/24", "Most home routers"),
            ("192.168.0.0/24", "Alternative home network"),
            ("10.0.0.0/24", "Common LAN"),
            ("172.16.0.0/24", "Docker default"),
            ("192.168.100.0/24", "IoT/Guest network"),
            ("10.10.0.0/24", "Lab network"),
        ]
        
        # Grid layout for better organization
        for i, (network, description) in enumerate(common_networks):
            row = i % 3
            col = i // 3
            
            btn_frame = ttk.Frame(common_frame)
            btn_frame.grid(row=row, column=col, padx=5, pady=2, sticky='w')
            
            ttk.Button(
                btn_frame, 
                text=f"+ {network}",
                command=lambda n=network: self.quick_add(n),
                width=15
            ).pack(side='left')
            
            ttk.Label(btn_frame, text=f" {description}", 
                     font=('Arial', 9), foreground='gray').pack(side='left')
        
        # Dialog buttons
        dialog_buttons = ttk.Frame(self.dialog)
        dialog_buttons.pack(fill='x', pady=10)
        
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
        if self.scanner.add_network(network):
            self.network_listbox.insert(tk.END, network)
            self.network_entry.delete(0, tk.END)
            self.network_entry.insert(0, "192.168.1.0")  # Reset to default
            messagebox.showinfo("Success", f"Added network: {network}")
        else:
            messagebox.showerror("Invalid Network", 
                               f"Invalid network address: {network}\n\n" +
                               "Please enter a valid network address")
    
    def quick_add(self, network):
        """Quick add a common network"""
        if self.scanner.add_network(network):
            # Check if already in list
            items = self.network_listbox.get(0, tk.END)
            if network not in items:
                self.network_listbox.insert(tk.END, network)
                messagebox.showinfo("Added", f"Added network: {network}")
            else:
                messagebox.showinfo("Already Added", f"{network} is already in the list")
    
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
