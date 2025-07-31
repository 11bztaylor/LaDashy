#!/usr/bin/env python3
"""
Homelab Documentation Wizard - Test Version
"""

import sys
import os

def check_environment():
    """Check if running in proper environment"""
    print("🔍 Checking environment...")
    
    # Check for required modules
    try:
        import paramiko
        print("✓ paramiko installed")
    except ImportError:
        print("✗ paramiko not found")
        
    try:
        import tkinter
        print("✓ tkinter available")
        
        # Test GUI
        if os.environ.get('DISPLAY'):
            print("✓ Display configured:", os.environ.get('DISPLAY'))
        else:
            print("⚠ No display configured")
    except ImportError:
        print("✗ tkinter not available")
    
    # Check if in WSL
    if os.path.exists('/proc/version'):
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                print("✓ Running in WSL")
    
    print("\nEnvironment check complete!")
    print("\nTo run the full tool:")
    print("1. Make sure you're in the virtual environment")
    print("2. Run: python homelab-wizard.py")

if __name__ == "__main__":
    check_environment()
