"""
Network configuration dialog - properly fixed version
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress

class NetworkConfigDialog:
    def __init__(self, parent, scanner):
        self.scanner = scanner
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Network Configuration")
        self.dialog.geometry("450x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Configure networks to scan for services:",
            font=('Arial', 10)
        )
        instructions.pack(pady=(0, 10))
        
        # Current networks frame
        list_frame = ttk.LabelFrame(main_frame, text="Networks to Scan", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Listbox for networks
        self.network_listbox = tk.Listbox(list_frame, height=6)
        self.network_listbox.pack(fill='both', expand=True)
        
        # Populate with current networks
        for network in self.scanner.get_networks():
            self.network_listbox.insert(tk.END, network)
        
        # Remove button
        ttk.Button(list_frame, text="Remove Selected", 
                  command=self.remove_network).pack(side='bottom', pady=(10, 0))
        
        # Add network frame
        add_frame = ttk.LabelFrame(main_frame, text="Add Network", padding=10)
        add_frame.pack(fill='x', pady=(0, 10))
        
        # Network input row
        input_row = ttk.Frame(add_frame)
        input_row.pack()
        
        ttk.Label(input_row, text="Network:").grid(row=0, column=0, padx=(0, 10))
        
        # IP address entry
        self.network_entry = ttk.Entry(input_row, width=15)
        self.network_entry.grid(row=0, column=1)
        self.network_entry.insert(0, "192.168.1.0")
        
        ttk.Label(input_row, text="/").grid(row=0, column=2, padx=5)
        
        # CIDR dropdown
        self.cidr_var = tk.StringVar(value="24")
        self.cidr_dropdown = ttk.Combobox(
            input_row, 
            textvariable=self.cidr_var,
            values=[str(i) for i in range(32, 7, -1)],
            width=4,
            state='readonly'
        )
        self.cidr_dropdown.grid(row=0, column=3)
        
        # Add button
        ttk.Button(input_row, text="Add", 
                  command=self.add_network).grid(row=0, column=4, padx=(20, 0))
        
        # Example text
        example_label = ttk.Label(add_frame, 
                                 text="Example: 192.168.1.0 /24", 
                                 font=('Arial', 9), 
                                 foreground='gray')
        example_label.pack(pady=(10, 0))
        
        # Close button at bottom
        ttk.Button(main_frame, text="Close", 
                  command=self.dialog.destroy).pack(side='bottom')
        
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
                # Clear the entry for next input
                self.network_entry.delete(0, tk.END)
                self.network_entry.insert(0, "192.168.1.0")
                messagebox.showinfo("Success", f"Added network: {network}")
            else:
                messagebox.showerror("Error", f"Failed to add network: {network}")
                
        except ValueError as e:
            messagebox.showerror("Invalid Network", 
                               f"Invalid network address: {network}\n\n"
                               f"Please use format like: 192.168.1.0/24")
    
    def remove_network(self):
        """Remove selected network"""
        selection = self.network_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a network to remove")
            return
        
        network = self.network_listbox.get(selection[0])
        
        # Confirm if it's the last network
        if self.network_listbox.size() == 1:
            response = messagebox.askyesno("Confirm", 
                                         "This is the last network. Remove it anyway?")
            if not response:
                return
        
        self.scanner.remove_network(network)
        self.network_listbox.delete(selection[0])
        messagebox.showinfo("Removed", f"Removed network: {network}")
