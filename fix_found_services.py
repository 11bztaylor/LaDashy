import sys

with open('homelab_wizard/gui/modern_main_window.py', 'r') as f:
    content = f.read()

# Fix the "Found 0 services" text - it should say "Ready" by default
status_label_section = content.find('self.status_label = ctk.CTkLabel(status_frame, text="Ready")')
if status_label_section == -1:
    # Find where status label is created
    status_section = content.find('self.status_label = ctk.CTkLabel(status_frame')
    if status_section != -1:
        # Make sure it says "Ready" not "Found 0 services"
        end_line = content.find(')', status_section)
        old_line = content[status_section:end_line+1]
        if 'Found 0 services' in old_line:
            new_line = old_line.replace('Found 0 services', 'Ready')
            content = content.replace(old_line, new_line)

# Also check if it's being set somewhere else
if 'Found 0 services' in content:
    content = content.replace('"Found 0 services"', '"Ready"')

with open('homelab_wizard/gui/modern_main_window.py', 'w') as f:
    f.write(content)

print("Fixed status text")
