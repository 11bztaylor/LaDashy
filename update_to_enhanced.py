import sys

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Change the import
content = content.replace(
    'from .service_list import ModernServiceList',
    'from .enhanced_service_list import EnhancedServiceList'
)

# Change the class name
content = content.replace(
    'self.service_list = ModernServiceList(',
    'self.service_list = EnhancedServiceList('
)

# Also update the window background
content = content.replace(
    'self.root.title("🏠 Homelab Documentation Wizard")',
    '''self.root.title("🏠 Homelab Documentation Wizard")
        self.root.configure(bg='#1e1e1e')'''
)

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Updated to use enhanced UI")
