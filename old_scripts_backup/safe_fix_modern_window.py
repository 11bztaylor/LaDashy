#!/usr/bin/env python3
"""Safer fix - ensure setup_documentation_tab checks for tab_view"""

import re

# Read the file
with open('homelab_wizard/gui/modern_main_window.py', 'r') as f:
    content = f.read()

# Find the setup_documentation_tab method
method_pattern = r'(def setup_documentation_tab\(self\):.*?)(?=\n    def|\nclass|\Z)'
method_match = re.search(method_pattern, content, re.DOTALL)

if method_match:
    method_content = method_match.group(1)
    
    # Add safety check at the beginning
    if 'if not hasattr(self' not in method_content:
        # Get the indentation
        lines = method_content.split('\n')
        indent = '        '  # Default to 8 spaces
        for line in lines[1:]:
            if line.strip():
                indent = line[:len(line) - len(line.lstrip())]
                break
        
        # Add safety check
        safety_check = f'\n{indent}# Safety check - ensure tab_view exists\n'
        safety_check += f'{indent}if not hasattr(self, "tab_view"):\n'
        safety_check += f'{indent}    print("Warning: tab_view not yet created, skipping documentation tab")\n'
        safety_check += f'{indent}    return\n'
        
        # Insert after the docstring
        docstring_end = method_content.find('"""', method_content.find('"""') + 3) + 3
        new_method = method_content[:docstring_end] + safety_check + method_content[docstring_end:]
        
        # Replace in content
        content = content.replace(method_content, new_method)
        
        # Write back
        with open('homelab_wizard/gui/modern_main_window.py', 'w') as f:
            f.write(content)
        
        print("✅ Added safety check to setup_documentation_tab()")

# Also ensure it's called at the right time
if 'self.setup_documentation_tab()' in content:
    # Check if it's called after setup_ui
    init_section = re.search(r'def __init__\(self.*?\):(.*?)(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    if init_section and 'setup_ui' in init_section.group(1):
        print("✅ setup_documentation_tab() is called after setup_ui()")
    else:
        print("⚠️  May need to move setup_documentation_tab() call after self.setup_ui()")

