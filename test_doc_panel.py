#!/usr/bin/env python3
"""Test documentation panel standalone"""
import customtkinter as ctk
from homelab_wizard.gui.documentation_panel import DocumentationPanel

# Test data
test_services = {
    "192.168.1.100": {
        "hostname": "unraid-server",
        "services": [
            {"name": "Plex", "ports": [32400], "confidence": 0.95},
            {"name": "Radarr", "ports": [7878], "confidence": 0.90}
        ]
    }
}

# Create test app
app = ctk.CTk()
app.title("Documentation Panel Test")
app.geometry("900x700")

# Create documentation panel
panel = DocumentationPanel(app, test_services, {}, {})
panel.pack(fill="both", expand=True, padx=10, pady=10)

print("Documentation panel test running...")
app.mainloop()
