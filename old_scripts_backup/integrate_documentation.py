#!/usr/bin/env python3
"""
Script to properly integrate documentation into modern_main_window.py
"""
import re

# Read the current file
with open('homelab_wizard/gui/modern_main_window.py', 'r') as f:
    content = f.read()

# Check if documentation panel is already imported
if 'from .documentation_panel import DocumentationPanel' not in content:
    # Add import after other imports
    import_line = "from .documentation_panel import DocumentationPanel"
    
    # Find the last import line
    import_matches = list(re.finditer(r'^from .*? import .*?$', content, re.MULTILINE))
    if import_matches:
        last_import_pos = import_matches[-1].end()
        content = content[:last_import_pos] + '\n' + import_line + content[last_import_pos:]
    print("✅ Added DocumentationPanel import")

# Find where tabs are created and add documentation tab
tab_creation_pattern = r'(self\.tab_view\.add\(["\'].*?["\']\))'
matches = list(re.finditer(tab_creation_pattern, content))

if matches and 'Documentation' not in content:
    # Add after the last tab
    last_tab_pos = matches[-1].end()
    doc_tab_line = '\n        self.tab_view.add("📄 Documentation")'
    content = content[:last_tab_pos] + doc_tab_line + content[last_tab_pos:]
    print("✅ Added Documentation tab")

# Find __init__ method and add documentation setup
init_method = re.search(r'def __init__\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
if init_method and 'setup_documentation_tab' not in content:
    # Add setup call at the end of __init__
    init_end = init_method.end()
    
    # Find the right indentation
    lines_after_init = content[init_method.start():init_end].split('\n')
    for line in lines_after_init[1:]:
        if line.strip() and not line.strip().startswith('#'):
            indent = len(line) - len(line.lstrip())
            break
    else:
        indent = 8
    
    setup_call = f'\n{" " * indent}# Setup documentation tab\n{" " * indent}self.setup_documentation_tab()\n'
    
    # Insert before the end of __init__
    content = content[:init_end-1] + setup_call + content[init_end-1:]
    print("✅ Added setup_documentation_tab() call")

# Add the setup method if it doesn't exist
if 'def setup_documentation_tab' not in content:
    setup_method = '''
    def setup_documentation_tab(self):
        """Setup documentation generation tab"""
        doc_frame = self.tab_view.tab("📄 Documentation")
        
        # Initialize empty data if needed
        if not hasattr(self, 'discovered_services'):
            self.discovered_services = {}
        if not hasattr(self, 'service_configs'):
            self.service_configs = {}
        if not hasattr(self, 'collected_data'):
            self.collected_data = {}
        
        # Create documentation panel
        self.doc_panel = DocumentationPanel(
            doc_frame,
            self.discovered_services,
            self.service_configs,
            self.collected_data
        )
        self.doc_panel.pack(fill="both", expand=True)
'''
    
    # Add before the last method or at the end of the class
    class_end = re.search(r'\nclass\s+\w+.*?:|$', content[content.find('class'):])
    if class_end:
        insert_pos = len(content) - 1
    else:
        insert_pos = len(content)
    
    content = content[:insert_pos] + setup_method + content[insert_pos:]
    print("✅ Added setup_documentation_tab() method")

# Write the updated file
with open('homelab_wizard/gui/modern_main_window.py', 'w') as f:
    f.write(content)

print("\n✅ Documentation integration complete!")
