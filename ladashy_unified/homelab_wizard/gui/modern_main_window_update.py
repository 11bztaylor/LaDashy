# Add this to the modern_main_window.py file:

# Import at the top
from .documentation_panel import DocumentationPanel

# Add to the UI setup method after creating other tabs:

# Documentation tab
self.doc_panel = DocumentationPanel(
    self.tab_view.tab("Documentation"),
    self.discovered_services,
    self.service_configs,
    self.collected_data
)
self.doc_panel.pack(fill="both", expand=True)

# Add method to update documentation panel when services change:
def update_documentation_panel(self):
    """Update documentation panel with current data"""
    if hasattr(self, 'doc_panel'):
        self.doc_panel.discovered_services = self.discovered_services
        self.doc_panel.service_configs = self.service_configs
        self.doc_panel.collected_data = self.collected_data
