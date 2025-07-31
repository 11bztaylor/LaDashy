import sys

with open('homelab_wizard/gui/config_panel.py', 'r') as f:
    lines = f.readlines()

# Find and fix the indentation issue
fixed_lines = []
for i, line in enumerate(lines):
    # Check if this is the problematic except line
    if line.strip() == 'except:' and i > 0:
        # Match the indentation of the try block
        # Look backwards for the corresponding try
        for j in range(i-1, -1, -1):
            if 'try:' in lines[j]:
                # Use the same indentation as the try
                indent = len(lines[j]) - len(lines[j].lstrip())
                fixed_lines.append(' ' * indent + 'except:\n')
                break
        else:
            # Default to 12 spaces if we can't find the try
            fixed_lines.append('            except:\n')
    else:
        fixed_lines.append(line)

with open('homelab_wizard/gui/config_panel.py', 'w') as f:
    f.writelines(fixed_lines)

print("Fixed indentation in config_panel.py")
