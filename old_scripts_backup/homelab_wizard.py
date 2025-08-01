#!/usr/bin/env python3
"""
Homelab Documentation Wizard
Main entry point with modern UI option
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for --modern flag
use_modern = "--classic" not in sys.argv  # Modern by default

if use_modern:
    from homelab_wizard.gui.modern_main_window import ModernHomelabWizard as HomelabWizard
else:
    from homelab_wizard.gui.main_window import HomelabWizard

def main():
    """Main entry point"""
    print(f"Starting Homelab Documentation Wizard... {'(Modern UI)' if use_modern else ''}")
    
    # Create and run the application
    app = HomelabWizard()
    app.run()

if __name__ == "__main__":
    main()
