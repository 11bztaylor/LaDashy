import sys
sys.path.insert(0, '.')

# Read scanner.py
with open('homelab_wizard/core/scanner.py', 'r') as f:
    content = f.read()

# Make sure we have the improved methods
if '_is_port_open' not in content:
    # Add the improved methods
    content += '''

def _is_port_open(self, host: str, port: int) -> bool:
    """Quick check if port is open with short timeout"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)  # Very short timeout for speed
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0
'''

# Save back
with open('homelab_wizard/core/scanner.py', 'w') as f:
    f.write(content)

print("Scanner updated with better port detection")
