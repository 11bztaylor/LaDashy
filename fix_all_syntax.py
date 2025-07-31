import sys

with open('homelab_wizard/gui/main_window.py', 'r') as f:
    content = f.read()

# Find the problematic line and fix it properly
if "header_frame = tk.Frame(self.root" in content:
    # Find the complete header frame section
    header_start = content.find("# Header")
    header_end = content.find("# Main notebook", header_start)
    
    if header_start != -1 and header_end != -1:
        # Replace with clean header code
        new_header = '''# Header
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🏠 Homelab Documentation Wizard",
                        font=('Arial', 24, 'bold'), bg='#2d2d2d', fg='white')
        title.pack(pady=20)
        
        '''
        content = content[:header_start] + new_header + content[header_end:]

with open('homelab_wizard/gui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed syntax errors")
