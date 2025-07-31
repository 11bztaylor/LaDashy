import sys
import re

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Find the create_header method
header_start = content.find('def create_header(self):')
if header_start != -1:
    # Find the end of the method
    next_method = content.find('\n    def ', header_start + 1)
    if next_method == -1:
        next_method = len(content)
    
    # Replace with clean header code
    new_header = '''def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame, 
            text="🏠 Homelab Documentation Wizard",
            font=('Arial', 24, 'bold'), 
            bg='#2d2d2d', 
            fg='white'
        )
        title.pack(pady=20)
        '''
    
    content = content[:header_start] + new_header + '\n    ' + content[next_method:]
else:
    # If no create_header method, look for the header creation in setup_gui
    setup_start = content.find('def setup_gui(self):')
    if setup_start != -1:
        # Find header frame creation
        header_pattern = r'header_frame\s*=.*?title\.pack\([^)]*\)'
        match = re.search(header_pattern, content[setup_start:], re.DOTALL)
        if match:
            old_header = match.group(0)
            new_header = '''header_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🏠 Homelab Documentation Wizard",
            font=('Arial', 24, 'bold'),
            bg='#2d2d2d',
            fg='white'
        )
        title.pack(pady=20)'''
            
            content = content[:setup_start] + content[setup_start:].replace(old_header, new_header, 1)

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed header section cleanly")
