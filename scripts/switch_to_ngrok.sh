#!/bin/bash

# Script to switch PecanTV iOS app to use ngrok tunnel
# Usage: ./scripts/switch_to_ngrok.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}🎬 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# API config file
API_CONFIG_FILE="PecanTV/PECANTV/PECANTV/Core/Config/APIConfig.swift"

print_status "Switching PecanTV iOS app to use ngrok tunnel"

# Check if API config file exists
if [ ! -f "$API_CONFIG_FILE" ]; then
    echo "❌ Error: API config file not found at $API_CONFIG_FILE"
    exit 1
fi

# Get current ngrok URL
print_status "Getting current ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'])" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    print_error "❌ Could not get ngrok URL. Is ngrok running?"
    echo "   Run: ngrok http 8000"
    exit 1
fi

print_status "Current ngrok URL: $NGROK_URL"

# Backup the original file
cp "$API_CONFIG_FILE" "${API_CONFIG_FILE}.backup"
print_success "Created backup: ${API_CONFIG_FILE}.backup"

# Update the baseURL to use ngrok
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|static let baseURL = \".*\"|static let baseURL = \"$NGROK_URL\"|g" "$API_CONFIG_FILE"
else
    # Linux
    sed -i "s|static let baseURL = \".*\"|static let baseURL = \"$NGROK_URL\"|g" "$API_CONFIG_FILE"
fi

print_success "Updated baseURL to use ngrok tunnel"

# Test the ngrok endpoint
print_status "Testing ngrok API endpoint..."
if curl -s "$NGROK_URL/health" > /dev/null; then
    print_success "ngrok API is responding correctly!"
else
    print_warning "ngrok API might not be ready yet"
fi

echo ""
print_status "Next steps:"
echo "1. Open your iOS project in Xcode"
echo "2. Build and run the app"
echo "3. The app will now connect to: $NGROK_URL"
echo ""
print_warning "To switch back to local development:"
echo "   ./scripts/switch_api_environment.sh local"
echo ""
print_warning "To switch to production:"
echo "   ./scripts/switch_to_render.sh"
echo ""
print_success "ngrok configuration complete!" 