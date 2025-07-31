# Read the file
with open('homelab-wizard.py', 'r') as f:
    content = f.read()

# Fix the syntax error - the line should be:
content = content.replace(
    'doc_content += f"\\n### {system_name}',
    'doc_content += f"\\n### {system_name}\\n'
)

# Make sure all multi-line f-strings are properly closed
# Write back
with open('homelab-wizard.py', 'w') as f:
    f.write(content)

print("Fixed! Try running again.")
