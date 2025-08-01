import sys

with open('homelab_wizard.py', 'r') as f:
    content = f.read()

# Change the default to use modern UI
content = content.replace(
    'use_modern = "--modern" in sys.argv',
    'use_modern = "--classic" not in sys.argv  # Modern by default'
)

with open('homelab_wizard.py', 'w') as f:
    f.write(content)

print("Modern UI is now the default!")
print("Use 'python homelab_wizard.py' for modern UI")
print("Use 'python homelab_wizard.py --classic' for classic UI")
