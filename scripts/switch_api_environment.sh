#!/bin/bash

# PecanTV API Environment Switcher
# This script helps you switch between different API environments

set -e

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

# API Configuration file path
API_CONFIG_FILE="PecanTV/PECANTV/PECANTV/Core/Config/APIConfig.swift"

# Environment configurations
LOCAL_URL="http://localhost:8000"
NGROK_URL="https://77b9-192-69-240-171.ngrok-free.app"
PRODUCTION_URL="https://api.pecantv.com"

# Function to switch API environment
switch_environment() {
    local environment=$1
    local new_url=""
    
    case $environment in
        "local")
            new_url=$LOCAL_URL
            print_status "Switching to LOCAL development environment"
            ;;
        "ngrok")
            new_url=$NGROK_URL
            print_status "Switching to NGROK tunnel environment"
            ;;
        "production")
            new_url=$PRODUCTION_URL
            print_status "Switching to PRODUCTION environment"
            ;;
        *)
            print_error "Invalid environment. Use: local, ngrok, or production"
            exit 1
            ;;
    esac
    
    # Create backup
    cp "$API_CONFIG_FILE" "${API_CONFIG_FILE}.backup"
    print_success "Backup created: ${API_CONFIG_FILE}.backup"
    
    # Update the baseURL in the config file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|static let baseURL = \".*\"|static let baseURL = \"$new_url\"|g" "$API_CONFIG_FILE"
    else
        # Linux
        sed -i "s|static let baseURL = \".*\"|static let baseURL = \"$new_url\"|g" "$API_CONFIG_FILE"
    fi
    
    print_success "Updated API base URL to: $new_url"
    
    # Test the new URL
    print_status "Testing new API endpoint..."
    if curl -s -f "$new_url/health" > /dev/null 2>&1; then
        print_success "API is responding at: $new_url/health"
    else
        print_warning "API not responding at: $new_url/health"
        print_warning "Make sure your API server is running for this environment"
    fi
}

# Function to show current environment
show_current() {
    print_status "Current API environment:"
    local current_url=$(grep "static let baseURL" "$API_CONFIG_FILE" | sed 's/.*"\(.*\)".*/\1/')
    echo "   URL: $current_url"
    
    # Test current URL
    print_status "Testing current endpoint..."
    if curl -s -f "$current_url/health" > /dev/null 2>&1; then
        print_success "✅ API is responding"
    else
        print_error "❌ API not responding"
    fi
}

# Function to show help
show_help() {
    echo -e "${BLUE}🎬 PecanTV API Environment Switcher${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  local       Switch to local development (localhost:8000)"
    echo "  ngrok       Switch to ngrok tunnel"
    echo "  production  Switch to production API"
    echo "  current     Show current environment"
    echo "  restore     Restore from backup"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local       # Switch to local development"
    echo "  $0 ngrok       # Switch to ngrok tunnel"
    echo "  $0 current     # Show current environment"
    echo ""
}

# Function to restore from backup
restore_backup() {
    if [ -f "${API_CONFIG_FILE}.backup" ]; then
        cp "${API_CONFIG_FILE}.backup" "$API_CONFIG_FILE"
        print_success "Restored from backup"
        show_current
    else
        print_error "No backup file found"
    fi
}

# Check if API config file exists
if [ ! -f "$API_CONFIG_FILE" ]; then
    print_error "API config file not found: $API_CONFIG_FILE"
    exit 1
fi

# Main script logic
case "${1:-help}" in
    "local")
        switch_environment "local"
        ;;
    "ngrok")
        switch_environment "ngrok"
        ;;
    "production")
        switch_environment "production"
        ;;
    "current")
        show_current
        ;;
    "restore")
        restore_backup
        ;;
    "help"|*)
        show_help
        ;;
esac 