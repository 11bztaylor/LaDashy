#!/usr/bin/env python3
"""Launch LaDashy with documentation feature enabled"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from homelab_wizard.gui.modern_main_window import ModernHomelabWizard

def main():
    """Main entry point with documentation enabled"""
    app = ModernHomelabWizard()
    
    # Enable documentation feature
    app.features['documentation'] = True
    
    app.run()

if __name__ == "__main__":
    main()
