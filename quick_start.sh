#!/bin/bash

# PecanTV Quick Start Script
# This script provides easy commands to set up and run the PecanTV project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🎬 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_success "Python $PYTHON_VERSION found"
        return 0
    elif command_exists python; then
        PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_success "Python $PYTHON_VERSION found"
        return 0
    else
        print_error "Python not found. Please install Python 3.8 or higher."
        return 1
    fi
}

# Function to install dependencies
install_deps() {
    print_status "Installing dependencies..."
    
    if command_exists pip3; then
        pip3 install -r requirements.txt
        pip3 install -r api/requirements.txt
    elif command_exists pip; then
        pip install -r requirements.txt
        pip install -r api/requirements.txt
    else
        print_error "pip not found. Please install pip."
        return 1
    fi
    
    print_success "Dependencies installed successfully"
}

# Function to start the API server
start_server() {
    print_status "Starting PecanTV API server..."
    
    if [ ! -f "api/main.py" ]; then
        print_error "main.py not found in api directory"
        return 1
    fi
    
    cd api
    
    print_success "API server starting on http://localhost:8000"
    print_success "API documentation: http://localhost:8000/docs"
    print_warning "Press Ctrl+C to stop the server"
    
    if command_exists python3; then
        python3 main.py
    else
        python main.py
    fi
}

# Function to run URL fixer
run_fixer() {
    print_status "Running URL fixer script..."
    
    if [ ! -f "scripts/fix_all_urls.py" ]; then
        print_error "fix_all_urls.py not found in scripts directory"
        return 1
    fi
    
    if command_exists python3; then
        python3 scripts/fix_all_urls.py
    else
        python scripts/fix_all_urls.py
    fi
}

# Function to test API
test_api() {
    print_status "Testing API endpoints..."
    
    # Check if curl is available
    if ! command_exists curl; then
        print_error "curl not found. Please install curl to test the API."
        return 1
    fi
    
    # Wait a moment for server to start if needed
    sleep 2
    
    # Test health endpoint
    if curl -s -f http://localhost:8000/health > /dev/null; then
        print_success "Health endpoint working"
    else
        print_error "Cannot connect to API. Make sure the server is running."
        return 1
    fi
    
    # Test content endpoint
    if curl -s -f http://localhost:8000/content > /dev/null; then
        print_success "Content endpoint working"
    else
        print_error "Content endpoint not working"
        return 1
    fi
    
    print_success "All API tests passed"
}

# Function to show help
show_help() {
    echo -e "${BLUE}🎬 PecanTV Quick Start Script${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install    Install dependencies"
    echo "  run        Start the API server"
    echo "  fix        Run URL fixer script"
    echo "  test       Test API endpoints"
    echo "  setup      Complete setup (install + test)"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install    # Install dependencies"
    echo "  $0 run        # Start server"
    echo "  $0 setup      # Complete setup"
    echo ""
}

# Function to run complete setup
complete_setup() {
    print_status "Running complete setup..."
    
    if ! check_python; then
        exit 1
    fi
    
    if ! install_deps; then
        exit 1
    fi
    
    print_success "Setup completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  1. Run '$0 run' to start the server"
    echo "  2. Run '$0 test' to test the API"
    echo "  3. Run '$0 fix' to fix URLs if needed"
    echo ""
}

# Main script logic
case "${1:-help}" in
    "install")
        check_python && install_deps
        ;;
    "run")
        start_server
        ;;
    "fix")
        run_fixer
        ;;
    "test")
        test_api
        ;;
    "setup")
        complete_setup
        ;;
    "help"|*)
        show_help
        ;;
esac 