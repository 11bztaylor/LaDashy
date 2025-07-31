import sys

with open('homelab_wizard/gui/modern_main_window.py', 'r') as f:
    content = f.read()

# Update imports
content = content.replace(
    'from .modern_ui import ModernServiceList, ModernConfigPanel',
    '''from .modern_ui_fixed import ModernServiceCard, ModernConfigPanel
import customtkinter as ctk'''
)

# Replace ModernServiceList with a custom implementation
service_list_code = '''
        # Service list frame
        service_frame = ctk.CTkFrame(left_panel)
        service_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Service list label
        list_label = ctk.CTkLabel(service_frame, text="Services", font=("Arial", 16, "bold"))
        list_label.pack(pady=(10, 5))
        
        # Scrollable frame for services
        self.service_scroll = ctk.CTkScrollableFrame(service_frame)
        self.service_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.service_cards = {}
        
        # Add all services
        for category, services in SERVICES.items():
            # Category header
            cat_label = ctk.CTkLabel(
                self.service_scroll,
                text=category,
                font=("Arial", 14, "bold"),
                anchor="w"
            )
            cat_label.pack(fill="x", padx=10, pady=(10, 5))
            
            # Service cards
            for service in services:
                card = ModernServiceCard(
                    self.service_scroll,
                    service["name"],
                    service.get("icon", "default"),
                    self.on_service_click,
                    self.on_service_toggle
                )
                card.pack(fill="x", padx=5, pady=2)
                self.service_cards[service["name"]] = card
'''

# Find and replace the service list section
list_start = content.find('# Service list')
list_end = content.find('# Right panel', list_start)
if list_start != -1 and list_end != -1:
    content = content[:list_start] + service_list_code + '\n        ' + content[list_end:]

# Update on_service_toggle to handle the checkbox state
toggle_update = '''def on_service_toggle(self, service_name, checked):
        """Handle service checkbox toggle"""
        self.service_vars[service_name].set(checked)
        if checked:
            self.on_service_click(service_name)'''

old_toggle = content.find('def on_service_toggle(self, service_name):')
if old_toggle != -1:
    toggle_end = content.find('\n    def ', old_toggle + 1)
    content = content[:old_toggle] + toggle_update + '\n\n    ' + content[toggle_end:]

with open('homelab_wizard/gui/modern_main_window.py', 'w') as f:
    f.write(content)

print("Updated modern main window")
