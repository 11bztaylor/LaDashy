#!/usr/bin/env python3
"""
Homelab Documentation Wizard
Main entry point
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homelab_wizard.gui.main_window import HomelabWizard

def main():
    """Main entry point"""
    print("Starting Homelab Documentation Wizard...")
    
    # Create and run the application
    app = HomelabWizard()
    app.run()

if __name__ == "__main__":
    main()
