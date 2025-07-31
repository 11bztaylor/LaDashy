import sys

with open('homelab_wizard/gui/network_config.py', 'r') as f:
    content = f.read()

# Fix the grab_set issue
old_grab = 'self.dialog.grab_set()'
new_grab = '''# Wait for window to be visible before grab
        self.dialog.update_idletasks()
        self.dialog.after(100, lambda: self.dialog.grab_set() if self.dialog.winfo_viewable() else None)'''

content = content.replace(old_grab, new_grab)

with open('homelab_wizard/gui/network_config.py', 'w') as f:
    f.write(content)

print("Fixed network dialog")
