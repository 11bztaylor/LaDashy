# This shows how to integrate the documentation panel into your existing modern UI

# Add this import at the top of modern_main_window.py:
from .documentation_panel import DocumentationPanel

# In the create_tabs method, add:
self.tab_view.add("Documentation")

# In the setup_documentation_tab method (create this):
def setup_documentation_tab(self):
    """Setup documentation generation tab"""
    doc_frame = self.tab_view.tab("Documentation")
    
    # Create documentation panel
    self.doc_panel = DocumentationPanel(
        doc_frame,
        self.discovered_services,
        self.service_configs,
        self.collected_data
    )
    self.doc_panel.pack(fill="both", expand=True, padx=10, pady=10)

# Call this in __init__ after creating other tabs:
self.setup_documentation_tab()

# When services are discovered or data is collected, update the panel:
def update_documentation_data(self):
    """Update documentation panel with latest data"""
    if hasattr(self, 'doc_panel'):
        self.doc_panel.discovered_services = self.discovered_services
        self.doc_panel.service_configs = self.service_configs  
        self.doc_panel.collected_data = self.collected_data
