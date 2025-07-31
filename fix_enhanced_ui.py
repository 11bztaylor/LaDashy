import sys

# First, let's check what happened to main_window.py
with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Make sure the header is visible
if "bg='#1e1e1e'" in content:
    # Update header to be visible
    header_section = content.find("header_frame = tk.Frame(self.root")
    if header_section != -1:
        # Find the end of this line
        line_end = content.find("\n", header_section)
        old_line = content[header_section:line_end]
        new_line = "header_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)"
        content = content.replace(old_line, new_line)

# Also make sure the header label is visible
content = content.replace(
    "title = tk.Label(header_frame, text=\"🏠 Homelab Documentation Wizard\",",
    "title = tk.Label(header_frame, text=\"🏠 Homelab Documentation Wizard\", bg='#2d2d2d', fg='white',"
)

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed visibility issues")
