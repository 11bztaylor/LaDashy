#!/usr/bin/env python3
"""
LaDashy Universal Launcher
Detects platform and launches appropriate interface
"""
import sys
import os
import platform
import subprocess

def launch_web():
    """Launch web interface"""
    print("Starting LaDashy Web Interface...")
    subprocess.run([sys.executable, "backend/api.py"])

def launch_desktop():
    """Launch desktop interface"""
    system = platform.system()
    
    if system == "Windows":
        print("Starting LaDashy Desktop (Windows)...")
        # Add the parent directory to Python path for imports
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        from homelab_wizard.gui.modern_main_window import ModernHomelabWizard
        app = ModernHomelabWizard()
        app.run()
    else:
        # For Mac/Linux, could use Electron or native
        print("Starting LaDashy Web Interface (Mac/Linux)...")
        launch_web()

def launch_docker():
    """Build and run Docker version"""
    print("Building LaDashy Docker container...")
    os.chdir("docker")
    subprocess.run(["docker-compose", "up", "--build"])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "web":
            launch_web()
        elif mode == "desktop":
            launch_desktop()
        elif mode == "docker":
            launch_docker()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python launch.py [web|desktop|docker]")
    else:
        # Auto-detect best mode
        if os.path.exists("/.dockerenv"):
            print("Running in Docker container")
            launch_web()
        elif platform.system() == "Windows":
            launch_desktop()
        else:
            launch_web()
