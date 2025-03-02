#!/usr/bin/env python3
"""
Setup script for Linux Troubleshooting Simulator
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        return False
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("\nIf you're encountering issues with Rust compilation, you have two options:")
        print("\n1. Install Rust:")
        if platform.system() == "Windows":
            print("   Download and run the installer from: https://rustup.rs/")
        else:
            print("   Run: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
            print("   Then: source $HOME/.cargo/env")
        
        print("\n2. Use the provided requirements.txt which uses an older version of pydantic")
        print("   that doesn't require Rust compilation.")
        
        return False

def setup_env_file():
    """Set up OpenAI API key as environment variable."""
    print("\nSetting up OpenAI API key...")
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ")
    if api_key:
        print(f"\nTo set your OpenAI API key, run the following command:")
        print(f"export OPENAI_API_KEY={api_key}")
        print("\nYou may want to add this to your shell profile (~/.bashrc, ~/.zshrc, etc.)")
        print("to make it persistent across terminal sessions.")
    else:
        print("\nSkipped API key setup. You'll need to set OPENAI_API_KEY later with:")
        print("export OPENAI_API_KEY=your_api_key")

def main():
    """Main setup function."""
    print("Setting up Linux Troubleshooting Simulator...")
    
    if not check_python_version():
        return
    
    if install_dependencies():
        setup_env_file()
        print("\nSetup completed successfully!")
        print("You can now run the application with: python main.py")
    else:
        print("\nSetup incomplete. Please resolve the issues above and try again.")

if __name__ == "__main__":
    main() 
