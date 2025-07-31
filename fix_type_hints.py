import os

# Fix type hints in all collector files
for root, dirs, files in os.walk('homelab_wizard/collectors'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Replace tuple[bool, str] with Tuple[bool, str]
            content = content.replace('tuple[bool, str]', 'Tuple[bool, str]')
            
            # Make sure Tuple is imported
            if 'Tuple[bool, str]' in content and 'from typing import' in content:
                if 'Tuple' not in content.split('from typing import')[1].split('\n')[0]:
                    content = content.replace('from typing import', 'from typing import Tuple,')
            
            with open(filepath, 'w') as f:
                f.write(content)

print("Fixed type hints for Python compatibility")
