"""
Manual service identification override
"""
import tkinter as tk
from tkinter import ttk, messagebox

class ServiceOverrideDialog:
    def __init__(self, parent, discovered_services):
        self.discovered_services = discovered_services
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Review Discovered Services")
        self.dialog.geometry("800x500")
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.changes = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI"""
        # Instructions
        instructions = ttk.Label(
            self.dialog,
            text="Review and correct service identifications if needed:",
            font=('Arial', 10)
        )
        instructions.pack(pady=10)
        
        # Service list
        list_frame = ttk.Frame(self.dialog)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('Service', 'Confidence', 'Port', 'Type')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        self.tree.heading('Service', text='Detected Service')
        self.tree.heading('Confidence', text='Confidence')
        self.tree.heading('Port', text='Port')
        self.tree.heading('Type', text='Device Type')
        
        self.tree.column('#0', width=200)
        self.tree.column('Service', width=150)
        self.tree.column('Confidence', width=100)
        self.tree.column('Port', width=80)
        self.tree.column('Type', width=100)
        
        # Populate tree
        for host, info in self.discovered_services.items():
            host_item = self.tree.insert('', 'end', text=f"{host} ({info['hostname']})")
            
            for service in info.get('services', []):
                confidence = service.get('confidence', 1.0)
                confidence_text = f"{confidence*100:.0f}%"
                
                # Color code by confidence
                tags = []
                if confidence < 0.7:
                    tags.append('low_confidence')
                elif confidence < 0.9:
                    tags.append('medium_confidence')
                else:
                    tags.append('high_confidence')
                
                self.tree.insert(
                    host_item, 'end',
                    values=(
                        service['name'],
                        confidence_text,
                        service['ports'][0],
                        service.get('device_type', 'unknown')
                    ),
                    tags=tags
                )
        
        # Configure tags
        self.tree.tag_configure('low_confidence', foreground='red')
        self.tree.tag_configure('medium_confidence', foreground='orange')
        self.tree.tag_configure('high_confidence', foreground='green')
        
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Controls
        control_frame = ttk.Frame(self.dialog)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(control_frame, text="Change Service", 
                  command=self.change_service).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Mark as Printer", 
                  command=self.mark_as_printer).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Remove Service", 
                  command=self.remove_service).pack(side='left', padx=5)
        
        # Dialog buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Accept", 
                  command=self.accept).pack(side='right', padx=20)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side='right')
    
    def change_service(self):
        """Change the service identification"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a service to change")
            return
        
        # Service selection dialog would go here
        messagebox.showinfo("Change Service", "Service change dialog would appear here")
    
    def mark_as_printer(self):
        """Mark device as printer"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device")
            return
        
        item = selection[0]
        if self.tree.parent(item) == '':  # It's a host item
            self.tree.item(item, values=('', '', '', 'printer'))
            # Remove all child services
            for child in self.tree.get_children(item):
                self.tree.delete(child)
    
    def remove_service(self):
        """Remove a service"""
        selection = self.tree.selection()
        if not selection:
            return
        
        self.tree.delete(selection[0])
    
    def accept(self):
        """Accept changes and close"""
        # Apply any changes made
        self.dialog.destroy()
