#!/usr/bin/env python3
"""
PecanTV Setup Script

This script helps set up the PecanTV project by installing dependencies
and providing easy commands to run the application.

Usage:
    python setup.py install    # Install dependencies
    python setup.py run        # Run the API server
    python setup.py fix        # Run URL fixer script
    python setup.py test       # Test the API
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Install root requirements
    if os.path.exists("requirements.txt"):
        if not run_command("pip install -r requirements.txt", "Installing root dependencies"):
            return False
    
    # Install API requirements
    if os.path.exists("api/requirements.txt"):
        if not run_command("pip install -r api/requirements.txt", "Installing API dependencies"):
            return False
    
    print("✅ All dependencies installed successfully")
    return True

def run_api():
    """Run the FastAPI server"""
    print("🚀 Starting PecanTV API server...")
    
    # Change to api directory
    os.chdir("api")
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found in api directory")
        return False
    
    # Run the server
    try:
        print("🌐 API server starting on http://localhost:8000")
        print("📖 API documentation available at http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error running server: {e}")
        return False
    
    return True

def run_fixer():
    """Run the URL fixer script"""
    print("🔧 Running URL fixer script...")
    
    if not os.path.exists("scripts/fix_all_urls.py"):
        print("❌ fix_all_urls.py not found in scripts directory")
        return False
    
    return run_command("python scripts/fix_all_urls.py", "Running URL fixer")

def test_api():
    """Test the API endpoints"""
    print("🧪 Testing API endpoints...")
    
    import requests
    import time
    
    # Wait a moment for server to start if needed
    time.sleep(2)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the API server is running (python setup.py run)")
        return False
    
    # Test content endpoint
    try:
        response = requests.get(f"{base_url}/content", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content endpoint working ({len(data)} items)")
        else:
            print(f"❌ Content endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing content endpoint: {e}")
        return False
    
    print("✅ All API tests passed")
    return True

def show_help():
    """Show help information"""
    print("""
🎬 PecanTV Setup Script

Usage:
    python setup.py install    # Install all dependencies
    python setup.py run        # Start the API server
    python setup.py fix        # Run URL fixer script
    python setup.py test       # Test API endpoints
    python setup.py help       # Show this help

Commands:
    install  - Install Python dependencies
    run      - Start the FastAPI server
    fix      - Run the comprehensive URL fixer
    test     - Test API endpoints
    help     - Show this help message

Examples:
    # First time setup
    python setup.py install
    
    # Start the server
    python setup.py run
    
    # Fix URLs in database
    python setup.py fix
    
    # Test the API
    python setup.py test
""")

def main():
    """Main entry point"""
    print("🎬 PecanTV Setup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Get command from arguments
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        if not install_dependencies():
            sys.exit(1)
        print("\n🎉 Setup completed successfully!")
        print("   Next steps:")
        print("   1. Run 'python setup.py run' to start the server")
        print("   2. Run 'python setup.py test' to test the API")
        print("   3. Run 'python setup.py fix' to fix URLs if needed")
    
    elif command == "run":
        if not run_api():
            sys.exit(1)
    
    elif command == "fix":
        if not run_fixer():
            sys.exit(1)
    
    elif command == "test":
        if not test_api():
            sys.exit(1)
    
    elif command == "help":
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 