"""
Documentation generation panel for LaDashy modern UI
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import json
import webbrowser

from ..generators.documentation_generator import DocumentationGenerator, generate_documentation

class DocumentationPanel(ctk.CTkFrame):
    """Documentation generation panel for the modern UI"""
    
    def __init__(self, parent, discovered_services: Dict, service_configs: Dict, collected_data: Dict):
        super().__init__(parent)
        
        self.discovered_services = discovered_services
        self.service_configs = service_configs
        self.collected_data = collected_data
        self.generator = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the documentation panel UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Documentation Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Stats
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(expand=True)
        
        # Calculate stats
        total_services = sum(len(h.get('services', [])) for h in self.discovered_services.values())
        configured_services = len([s for s in self.service_configs if self.service_configs[s]])
        
        # Stat cards
        self._create_stat_card(stats_container, "Total Services", str(total_services), "#4ecdc4").pack(side="left", padx=10)
        self._create_stat_card(stats_container, "Configured", str(configured_services), "#96ceb4").pack(side="left", padx=10)
        self._create_stat_card(stats_container, "Hosts", str(len(self.discovered_services)), "#45b7d1").pack(side="left", padx=10)
        
        # Options
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            options_frame,
            text="Documentation Options",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Create two columns
        options_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_container.pack(fill="both", expand=True, padx=20)
        
        left_column = ctk.CTkFrame(options_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_column = ctk.CTkFrame(options_container, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Options
        self.options = {
            'network_topology': ctk.BooleanVar(value=True),
            'service_dependencies': ctk.BooleanVar(value=True),
            'docker_compose': ctk.BooleanVar(value=True),
            'security_audit': ctk.BooleanVar(value=True),
            'backup_status': ctk.BooleanVar(value=True),
            'api_documentation': ctk.BooleanVar(value=True)
        }
        
        # Left column options
        ctk.CTkCheckBox(
            left_column,
            text="Network Topology Diagram",
            variable=self.options['network_topology'],
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=5)
        
        ctk.CTkCheckBox(
            left_column,
            text="Service Dependencies Map",
            variable=self.options['service_dependencies'],
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=5)
        
        ctk.CTkCheckBox(
            left_column,
            text="Docker Compose Files",
            variable=self.options['docker_compose'],
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=5)
        
        # Right column options
        ctk.CTkCheckBox(
            right_column,
            text="Security Audit Report",
            variable=self.options['security_audit'],
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=5)
        
        ctk.CTkCheckBox(
            right_column,
            text="Backup Configuration",
            variable=self.options['backup_status'],
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=5)
        
        ctk.CTkCheckBox(
            right_column,
            text="API Documentation",
            variable=self.options['api_documentation'],
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=5)
        
        # Output formats
        format_frame = ctk.CTkFrame(self)
        format_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            format_frame,
            text="Output Formats",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        format_container = ctk.CTkFrame(format_frame, fg_color="transparent")
        format_container.pack(fill="x", padx=20, pady=(0, 20))
        
        self.formats = {
            'markdown': ctk.BooleanVar(value=True),
            'html': ctk.BooleanVar(value=True),
            'json': ctk.BooleanVar(value=True),
            'pdf': ctk.BooleanVar(value=False)
        }
        
        ctk.CTkCheckBox(
            format_container,
            text="Markdown",
            variable=self.formats['markdown'],
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        ctk.CTkCheckBox(
            format_container,
            text="HTML Dashboard",
            variable=self.formats['html'],
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        ctk.CTkCheckBox(
            format_container,
            text="JSON Export",
            variable=self.formats['json'],
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        # Output directory
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            output_frame,
            text="Output Directory",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        dir_container = ctk.CTkFrame(output_frame, fg_color="transparent")
        dir_container.pack(fill="x", padx=20, pady=(0, 20))
        
        self.output_dir = ctk.StringVar(value=str(Path.home() / "homelab_docs"))
        
        self.dir_entry = ctk.CTkEntry(
            dir_container,
            textvariable=self.output_dir,
            width=400,
            font=ctk.CTkFont(size=14)
        )
        self.dir_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            dir_container,
            text="Browse",
            width=100,
            command=self.browse_directory
        ).pack(side="left")
        
        # Generate button
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.generate_button = ctk.CTkButton(
            button_frame,
            text="Generate Documentation",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            command=self.generate_documentation
        )
        self.generate_button.pack(expand=True)
        
        # Progress section (initially hidden)
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        
    def _create_stat_card(self, parent, title, value, color):
        """Create a stat card widget"""
        card = ctk.CTkFrame(parent)
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="#808080"
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        ).pack(pady=(0, 10))
        
        return card
    
    def browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)
    
    def generate_documentation(self):
        """Start documentation generation"""
        # Validate inputs
        if not any(self.formats[fmt].get() for fmt in self.formats):
            messagebox.showwarning("No Format Selected", "Please select at least one output format.")
            return
        
        # Show progress
        self.progress_frame.pack(fill="x", padx=20, pady=10, before=self.generate_button.master)
        self.progress_label.pack(pady=5)
        self.progress_bar.pack(pady=5)
        self.progress_label.configure(text="Generating documentation...")
        self.progress_bar.set(0)
        self.generate_button.configure(state="disabled")
        
        # Start generation in thread
        thread = threading.Thread(target=self._generate_worker, daemon=True)
        thread.start()
    
    def _generate_worker(self):
        """Worker thread for documentation generation"""
        try:
            output_dir = self.output_dir.get()
            
            # Update progress
            self.progress_bar.set(0.1)
            self.progress_label.configure(text="Creating documentation structure...")
            
            # Generate documentation
            results = generate_documentation(
                self.discovered_services,
                self.service_configs,
                self.collected_data,
                output_dir
            )
            
            # Update progress
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="Documentation generated successfully!")
            
            # Show completion dialog
            self.after(1000, self._generation_complete, output_dir)
            
        except Exception as e:
            self.after(0, self._generation_error, str(e))
    
    def _generation_complete(self, output_dir):
        """Handle generation completion"""
        self.generate_button.configure(state="normal")
        
        # Ask to open documentation
        if messagebox.askyesno("Documentation Generated", 
                              f"Documentation has been generated successfully!\n\n"
                              f"Location: {output_dir}\n\n"
                              f"Would you like to open the documentation now?"):
            # Open HTML dashboard if generated
            dashboard_path = Path(output_dir) / "dashboard.html"
            if dashboard_path.exists():
                webbrowser.open(f"file://{dashboard_path}")
            else:
                # Open the directory
                import platform
                if platform.system() == "Windows":
                    import os
                    os.startfile(output_dir)
                elif platform.system() == "Darwin":
                    import subprocess
                    subprocess.run(["open", output_dir])
                else:
                    import subprocess
                    subprocess.run(["xdg-open", output_dir])
    
    def _generation_error(self, error):
        """Handle generation error"""
        self.generate_button.configure(state="normal")
        self.progress_frame.pack_forget()
        messagebox.showerror("Generation Error", f"Failed to generate documentation:\n\n{error}")
