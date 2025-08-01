#!/bin/bash
# Integrate documentation generation into LaDashy's modern UI

cd /home/zach/homelab-documentation

echo "Adding Documentation tab to modern UI..."

# First, let's find and update the modern_main_window.py file
MAIN_WINDOW_FILE=$(find . -name "modern_main_window.py" -path "*/gui/*" | head -1)

if [ -z "$MAIN_WINDOW_FILE" ]; then
    echo "Could not find modern_main_window.py, checking for other UI files..."
    find . -name "*.py" -path "*/gui/*" | grep -E "(main|window|ui)" | head -10
else
    echo "Found main window file: $MAIN_WINDOW_FILE"
    
    # Create a backup
    cp "$MAIN_WINDOW_FILE" "${MAIN_WINDOW_FILE}.backup"
    
    # Add import for documentation panel at the top of the file
    sed -i '1a from .documentation_panel import DocumentationPanel' "$MAIN_WINDOW_FILE"
    
    echo "✅ Added documentation panel import"
fi

# Let's create a simple integration example
cat > homelab_wizard/gui/add_documentation_tab.py << 'EOFPY'
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
EOFPY

# Let's also check what UI files exist
echo -e "\n=== UI Files Found ==="
find homelab_wizard/gui -name "*.py" -type f | sort

# Create a quick test to run the app with documentation
cat > run_with_docs.py << 'EOFRUN'
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
EOFRUN

chmod +x run_with_docs.py

echo -e "\n✅ Integration scripts created!"
echo -e "\nTo run LaDashy with documentation tab:"
echo "./run_with_docs.py"
