"""
Instructions to add documentation tab to your modern UI
"""

# Add this method to your ModernMainWindow class:

def setup_documentation_tab(self):
    """Setup documentation generation tab"""
    # Add tab
    self.tab_view.add("📄 Documentation")
    doc_frame = self.tab_view.tab("📄 Documentation")
    
    # Create documentation panel
    self.doc_panel = DocumentationPanel(
        doc_frame,
        self.discovered_services,
        self.service_configs,
        self.collected_data
    )
    self.doc_panel.pack(fill="both", expand=True)

# Call this in your __init__ method after creating other tabs:
# self.setup_documentation_tab()

# When you update services, also update the documentation panel:
def update_services(self):
    """Update services and documentation panel"""
    # ... existing code ...
    
    # Update documentation panel
    if hasattr(self, 'doc_panel'):
        self.doc_panel.discovered_services = self.discovered_services
        self.doc_panel.service_configs = self.service_configs
        self.doc_panel.collected_data = self.collected_data
