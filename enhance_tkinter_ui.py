import sys

with open('homelab_wizard/gui/service_list.py', 'r') as f:
    content = f.read()

# Add better colors and styling
new_colors = '''
        # Modern color scheme
        self.colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d',
            'bg_hover': '#3d3d3d',
            'bg_selected': '#0d7377',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#14ffec',
            'success': '#4caf50',
            'error': '#f44336',
            'warning': '#ff9800'
        }
'''

# Insert after setup_ui
setup_pos = content.find('def setup_ui(self):')
next_line = content.find('\n', setup_pos)
next_line = content.find('\n', next_line + 1)
content = content[:next_line] + new_colors + content[next_line:]

# Update canvas background
content = content.replace(
    "self.canvas = tk.Canvas(self.parent, bg='#f0f0f0'",
    "self.canvas = tk.Canvas(self.parent, bg='#1a1a1a'"
)

# Update category header styling
content = content.replace(
    "category_container = tk.Frame(self.scrollable_frame, bg='white'",
    "category_container = tk.Frame(self.scrollable_frame, bg='#2d2d2d'"
)

content = content.replace(
    "header_frame = tk.Frame(category_container, bg='#e0e0e0'",
    "header_frame = tk.Frame(category_container, bg='#3d3d3d'"
)

# Update service frame styling
content = content.replace(
    "service_frame = tk.Frame(parent, bg='white'",
    "service_frame = tk.Frame(parent, bg='#2d2d2d'"
)

# Update text colors
content = content.replace(
    'font=(\'Arial\', 11, \'bold\'), bg=\'#e0e0e0\'',
    'font=(\'Arial\', 11, \'bold\'), bg=\'#3d3d3d\', fg=\'#ffffff\''
)

with open('homelab_wizard/gui/service_list.py', 'w') as f:
    f.write(content)

print("Enhanced tkinter UI styling")
