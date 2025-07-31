import sys

with open('homelab_wizard/gui/config_panel.py', 'r') as f:
    content = f.read()

# Update the test_connection method to notify main window
old_test_end = 'self.status_label.config(text=f"✗ {message}", foreground=\'red\')'
new_test_end = '''self.status_label.config(text=f"✗ {message}", foreground='red')
            # Notify main window
            main_window = self.parent.master.master  # Navigate up to main window
            if hasattr(main_window, 'update_service_status'):
                main_window.update_service_status(self.current_service, 'error')'''

content = content.replace(old_test_end, new_test_end)

# Update success case too
old_success = 'self.status_label.config(text=f"✓ {message}", foreground=\'green\')'
new_success = '''self.status_label.config(text=f"✓ {message}", foreground='green')
            # Notify main window
            main_window = self.parent.master.master  # Navigate up to main window
            if hasattr(main_window, 'update_service_status'):
                main_window.update_service_status(self.current_service, 'connected')'''

content = content.replace(old_success, new_success)

# Update save_config to mark as configured
save_success = content.find('self.service_label.config(text=f"✓ {self.current_service} configuration saved!")')
if save_success != -1:
    insert_pos = content.find('\n', save_success)
    new_code = '''
        
        # Mark as configured in main window
        main_window = self.parent.master.master
        if hasattr(main_window, 'update_service_status'):
            main_window.update_service_status(self.current_service, 'configured')'''
    content = content[:insert_pos] + new_code + content[insert_pos:]

with open('homelab_wizard/gui/config_panel.py', 'w') as f:
    f.write(content)

print("Config panel updated!")
