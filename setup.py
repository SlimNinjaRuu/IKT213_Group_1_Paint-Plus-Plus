#!/usr/bin/env python3
"""
Setup script for Photo Editor Application
"""

import sys
import subprocess
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible. Please use Python 3.7 or higher")
        return False

def main():
    """Main setup function"""
    print("Photo Editor Application Setup")
    print("=" * 40)
    
    if not check_python_version():
        sys.exit(1)
    
    if not install_requirements():
        sys.exit(1)
    
    print("\n✓ Setup completed successfully!")
    print("\nTo run the application:")
    print("  python photo_editor.py")
    print("\nOr:")
    print("  python3 photo_editor.py")

if __name__ == "__main__":
    main()