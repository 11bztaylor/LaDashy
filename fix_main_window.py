import sys

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Find where create_service_list is called and ensure service_vars is populated first
create_list_section = content.find('def create_service_list(self, parent):')
if create_list_section != -1:
    # Find the section where we create the service list
    new_method = '''def create_service_list(self, parent):
        """Create the modern service selection list"""
        from ..services.definitions import SERVICES
        
        # Initialize service_vars first
        for category, services in SERVICES.items():
            for service in services:
                if service["name"] not in self.service_vars:
                    self.service_vars[service["name"]] = tk.BooleanVar()
        
        # Create modern service list
        self.service_list = ModernServiceList(
            parent, 
            self.service_vars,
            self.on_service_click,
            self.on_service_toggle
        )
        
        # Add all categories and services
        for category, services in SERVICES.items():
            self.service_list.add_category(category, services)'''
    
    # Find the end of the method
    method_end = content.find('\n    def ', create_list_section + 1)
    if method_end == -1:
        method_end = content.find('\n\n', create_list_section)
    
    content = content[:create_list_section] + new_method + content[method_end:]

# Also add the missing tk import if needed
if 'import tkinter as tk' not in content:
    import_section = content.find('import tkinter')
    if import_section == -1:
        # Add after other imports
        import_section = content.find('from tkinter import')
        content = 'import tkinter as tk\n' + content

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed main_window.py")
