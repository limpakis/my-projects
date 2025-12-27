#!/usr/bin/env python3
"""
RLFAP Project Setup Script

Setup verification for the CSP solver.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    try:
        import sortedcontainers
        print("✅ sortedcontainers: OK")
        return True
    except ImportError:
        print("❌ sortedcontainers: Missing")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Please run: pip install -r requirements.txt")
            return False

def check_project_structure():
    """Verify project structure is correct."""
    print("\n🏗️  Checking project structure...")
    
    required_dirs = ['src', 'scripts', 'data', 'examples']
    required_files = [
        'README.md', 
        'requirements.txt',
        'demo.py',
        'src/csp.py',
        'src/rlfap.py', 
        'scripts/main.py'
    ]
    
    missing = []
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing.append(f"Directory: {dir_name}")
    
    for file_name in required_files:
        if not os.path.exists(file_name):
            missing.append(f"File: {file_name}")
    
    if missing:
        print("❌ Missing components:")
        for item in missing:
            print(f"   - {item}")
        return False
    else:
        print("✅ Project structure: OK")
        return True

def check_data_files():
    """Check if RLFAP data files are present."""
    print("\n📊 Checking RLFAP data files...")
    
    data_files = os.listdir('data')
    var_files = [f for f in data_files if f.startswith('var')]
    dom_files = [f for f in data_files if f.startswith('dom')]
    ctr_files = [f for f in data_files if f.startswith('ctr')]
    
    print(f"   Variables files: {len(var_files)}")
    print(f"   Domains files: {len(dom_files)}")
    print(f"   Constraints files: {len(ctr_files)}")
    
    if len(var_files) > 0 and len(dom_files) > 0 and len(ctr_files) > 0:
        print("✅ RLFAP data files: OK")
        return True
    else:
        print("❌ Missing RLFAP data files")
        return False

def run_demo():
    """Run a quick demo to verify functionality."""
    print("\n🎯 Running quick demo...")
    try:
        subprocess.check_call([sys.executable, "demo.py"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        print("✅ Demo: OK")
        return True
    except subprocess.CalledProcessError:
        print("❌ Demo failed")
        return False

def main():
    print("RLFAP CSP Solver - Setup Check")
    print("=" * 35)
    
    checks = [
        check_dependencies(),
        check_project_structure(), 
        check_data_files(),
        run_demo()
    ]
    
    print("\n" + "=" * 35)
    if all(checks):
        print("Setup complete! Project is ready.")
        print("\nQuick start:")
        print("   python demo.py          # Run demo")
        print("   python scripts/main.py  # Full benchmark")
        print("   make help               # Show all commands")
    else:
        print("Setup issues found. Please fix the problems above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())