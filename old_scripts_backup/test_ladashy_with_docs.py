#!/usr/bin/env python3
"""Test LaDashy with documentation feature"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
try:
    from homelab_wizard.gui.modern_main_window import ModernHomelabWizard
    
    print("Starting LaDashy with documentation feature...")
    app = ModernHomelabWizard()
    app.run()
    
except ImportError as e:
    print(f"Import error: {e}")
    print("\nTrying alternative import...")
    
    # Try the actual class name that might be used
    try:
        from homelab_wizard.gui.modern_ui_fixed import ModernHomelabDashboard
        app = ModernHomelabDashboard()
        app.mainloop()
    except:
        print("Could not find the main application class")
        print("\nAvailable UI files:")
        import glob
        for f in glob.glob("homelab_wizard/gui/*.py"):
            print(f"  - {f}")
