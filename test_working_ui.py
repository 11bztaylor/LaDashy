#!/usr/bin/env python3
"""Minimal working version to test"""
import customtkinter as ctk
from homelab_wizard.gui.documentation_panel import DocumentationPanel

class MinimalLaDashy(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("LaDashy - Minimal Test")
        self.geometry("1200x800")
        
        # Create tab view FIRST
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_view.add("Services")
        self.tab_view.add("Documentation")
        
        # Simple services tab
        services_label = ctk.CTkLabel(self.tab_view.tab("Services"), text="Services will appear here")
        services_label.pack(pady=20)
        
        # Documentation tab
        self.discovered_services = {
            "192.168.1.100": {
                "hostname": "test-server",
                "services": [{"name": "Plex", "ports": [32400]}]
            }
        }
        self.service_configs = {}
        self.collected_data = {}
        
        doc_panel = DocumentationPanel(
            self.tab_view.tab("Documentation"),
            self.discovered_services,
            self.service_configs,
            self.collected_data
        )
        doc_panel.pack(fill="both", expand=True)
        
        print("✅ Minimal UI started successfully!")

if __name__ == "__main__":
    app = MinimalLaDashy()
    app.mainloop()
