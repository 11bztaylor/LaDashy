#!/usr/bin/env python3
"""
Homelab Documentation Wizard - Fixed Version
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform
import os
import sys

print("🏠 Homelab Documentation Wizard")
print("=" * 50)

# Create main window
root = tk.Tk()
root.title("🏠 Homelab Documentation Wizard")
root.geometry("900x600")

# Header
header_frame = tk.Frame(root, bg='#1e1e1e', height=80)
header_frame.pack(fill='x')
header_frame.pack_propagate(False)

title = tk.Label(header_frame, text="🏠 Homelab Documentation Wizard", 
                font=('Arial', 24, 'bold'), bg='#1e1e1e', fg='white')
title.pack(pady=20)

# Main content
content_frame = ttk.Frame(root)
content_frame.pack(fill='both', expand=True, padx=20, pady=20)

# Welcome message
welcome_text = """Welcome to the Homelab Documentation Wizard!

This tool will help you document your self-hosted services.

Select your services below:"""

ttk.Label(content_frame, text=welcome_text, font=('Arial', 12)).pack(pady=20)

# Service checkboxes
services_frame = ttk.LabelFrame(content_frame, text="Services", padding=20)
services_frame.pack(fill='both', expand=True)

# Sample services
services = {
    "Docker": tk.BooleanVar(value=True),
    "Plex": tk.BooleanVar(),
    "Jellyfin": tk.BooleanVar(),
    "Radarr": tk.BooleanVar(),
    "Sonarr": tk.BooleanVar(),
    "Nginx Proxy Manager": tk.BooleanVar(),
    "Portainer": tk.BooleanVar(value=True),
    "Pi-hole": tk.BooleanVar(),
    "Home Assistant": tk.BooleanVar(),
    "Nextcloud": tk.BooleanVar(),
}

# Create checkboxes in a grid
row = 0
col = 0
for service, var in services.items():
    cb = ttk.Checkbutton(services_frame, text=service, variable=var)
    cb.grid(row=row, column=col, padx=10, pady=5, sticky='w')
    col += 1
    if col > 2:
        col = 0
        row += 1

# Buttons
button_frame = ttk.Frame(root)
button_frame.pack(fill='x', padx=20, pady=20)

def generate_docs():
    selected = [name for name, var in services.items() if var.get()]
    if selected:
        msg = f"Generating documentation for:\n" + "\n".join(f"• {s}" for s in selected)
        messagebox.showinfo("Generating", msg)
        
        # Create output directory
        output_dir = os.path.expanduser("~/homelab-docs")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a simple README
        readme_content = f"""# Homelab Documentation

Generated: {os.popen('date').read().strip()}

## Services Documented

"""
        for service in selected:
            readme_content += f"- {service}\n"
            
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
            
        messagebox.showinfo("Complete", f"Documentation saved to:\n{output_dir}")
    else:
        messagebox.showwarning("No Selection", "Please select at least one service")

generate_btn = ttk.Button(button_frame, text="🚀 Generate Documentation", 
                         command=generate_docs)
generate_btn.pack(side='right')

# Run the GUI
root.mainloop()
