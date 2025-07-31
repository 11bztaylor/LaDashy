#!/usr/bin/env python3
"""Run LaDashy with documentation feature"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import the modern UI
try:
    from homelab_wizard.gui.modern_main_window import ModernHomelabWizard as MainApp
    print("Using ModernHomelabWizard")
except ImportError:
    try:
        from homelab_wizard.gui.main_window import HomelabWizard as MainApp
        print("Using HomelabWizard")
    except ImportError:
        print("Could not find main application class")
        sys.exit(1)

# Monkey patch to add documentation tab
original_init = MainApp.__init__

def new_init(self):
    original_init(self)
    
    # Try to add documentation tab
    try:
        from homelab_wizard.gui.documentation_panel import DocumentationPanel
        
        # Add documentation tab if we have a tab view
        if hasattr(self, 'tab_view'):
            self.tab_view.add("📄 Documentation")
            doc_frame = self.tab_view.tab("📄 Documentation")
            
            # Initialize with empty data if needed
            if not hasattr(self, 'discovered_services'):
                self.discovered_services = {}
            if not hasattr(self, 'service_configs'):
                self.service_configs = {}
            if not hasattr(self, 'collected_data'):
                self.collected_data = {}
            
            self.doc_panel = DocumentationPanel(
                doc_frame,
                self.discovered_services,
                self.service_configs,
                self.collected_data
            )
            self.doc_panel.pack(fill="both", expand=True)
            print("✅ Documentation tab added!")
    except Exception as e:
        print(f"Could not add documentation tab: {e}")

MainApp.__init__ = new_init

# Run the app
if __name__ == "__main__":
    app = MainApp()
    app.run()
