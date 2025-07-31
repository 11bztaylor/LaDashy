import sys

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Find and fix the repeated bg argument
if "bg='#1e1e1e', fg='white')" in content and "bg='#2d2d2d'" in content:
    # The issue is likely a duplicate bg argument
    content = content.replace(
        "font=('Arial', 24, 'bold'), bg='#1e1e1e', fg='white')",
        "font=('Arial', 24, 'bold'), fg='white')"
    )

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed syntax error")
