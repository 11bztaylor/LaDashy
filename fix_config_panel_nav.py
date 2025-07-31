import sys

with open('homelab_wizard/gui/config_panel.py', 'r') as f:
    content = f.read()

# Fix the navigation to main window
old_nav = 'main_window = self.parent.master.master  # Navigate up to main window'
new_nav = '''# Navigate up to main window - handle different widget hierarchies
            try:
                # Try different paths to find main window
                main_window = self.parent
                while main_window and not hasattr(main_window, 'update_service_status'):
                    main_window = getattr(main_window, 'master', None)
            except:
                main_window = None'''

content = content.replace(old_nav, new_nav)

# Apply the same fix to all instances
content = content.replace(
    'main_window = self.parent.master.master',
    '''try:
                main_window = self.parent
                while main_window and not hasattr(main_window, 'update_service_status'):
                    main_window = getattr(main_window, 'master', None)
            except:
                main_window = None'''
)

with open('homelab_wizard/gui/config_panel.py', 'w') as f:
    f.write(content)

print("Fixed config_panel.py navigation")
