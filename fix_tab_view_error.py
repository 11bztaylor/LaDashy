#!/usr/bin/env python3
"""Fix the tab_view initialization error"""

# Read the file
with open('homelab_wizard/gui/modern_main_window.py', 'r') as f:
    lines = f.readlines()

# Find where setup_documentation_tab is called
init_call_line = None
for i, line in enumerate(lines):
    if 'self.setup_documentation_tab()' in line and 'def' not in line:
        init_call_line = i
        print(f"Found setup_documentation_tab() call at line {i+1}")
        break

# Find where tab_view is created
tab_view_line = None
for i, line in enumerate(lines):
    if 'self.tab_view' in line and '=' in line and 'CTkTabview' in line:
        tab_view_line = i
        print(f"Found tab_view creation at line {i+1}")
        break

# Find setup_ui method
setup_ui_line = None
for i, line in enumerate(lines):
    if 'def setup_ui' in line:
        setup_ui_line = i
        print(f"Found setup_ui method at line {i+1}")
        break

# If we found the call before tab_view creation, we need to move it
if init_call_line and tab_view_line and init_call_line < tab_view_line:
    print("\n❌ setup_documentation_tab() is called before tab_view exists!")
    
    # Remove the line
    doc_setup_line = lines[init_call_line]
    lines.pop(init_call_line)
    
    # Find the end of setup_ui method or a good place after tab_view
    insert_line = None
    
    # Look for the end of the method that creates tab_view
    indent_level = len(doc_setup_line) - len(doc_setup_line.lstrip())
    
    # Find a good insertion point after tab_view is created
    for i in range(tab_view_line + 1, len(lines)):
        line = lines[i]
        # Look for the next method definition or class
        if line.strip() and not line.startswith(' '):
            insert_line = i - 1
            break
        # Or look for a line with same indentation after some tab setup
        if 'self.tab_view.add' in line:
            # Find the last tab addition
            for j in range(i + 1, len(lines)):
                if 'self.tab_view.add' not in lines[j]:
                    insert_line = j
                    break
    
    if not insert_line:
        # Insert at the end of the file
        insert_line = len(lines) - 1
    
    # Insert the documentation setup call
    print(f"\n✅ Moving setup_documentation_tab() call to line {insert_line + 1}")
    lines.insert(insert_line, doc_setup_line)
    
    # Write the fixed file
    with open('homelab_wizard/gui/modern_main_window.py', 'w') as f:
        f.writelines(lines)
    
    print("\n✅ Fixed! The setup_documentation_tab() call has been moved after tab_view creation.")
else:
    print("\n✅ No fix needed or unable to determine issue automatically.")
    print("Please check the file manually.")

