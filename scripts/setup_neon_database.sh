#!/bin/bash

# PecanTV Neon Database Setup Script
# This script helps you configure the Neon database connection for production

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

# API directory
API_DIR="api"
ENV_FILE="$API_DIR/.env"
ENV_EXAMPLE="$API_DIR/env.example"

print_status "Setting up Neon database connection for PecanTV API"

# Check if .env file exists
if [ -f "$ENV_FILE" ]; then
    print_warning ".env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled"
        exit 0
    fi
fi

# Create .env file
print_status "Creating .env file..."

# Copy example if it exists
if [ -f "$ENV_EXAMPLE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    print_success "Copied env.example to .env"
else
    # Create basic .env file
    cat > "$ENV_FILE" << EOF
# PecanTV API Environment Configuration
# Database Configuration
DATABASE_URL=your_neon_database_url_here

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_webhook_secret_here

# JWT Configuration
JWT_SECRET=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# Logging
LOG_LEVEL=INFO
EOF
    print_success "Created basic .env file"
fi

print_status "Next steps to complete Neon database setup:"
echo ""
print_warning "1. Get your Neon database URL:"
echo "   - Go to https://console.neon.tech"
echo "   - Select your project"
echo "   - Go to 'Connection Details'"
echo "   - Copy the 'Pooled connection' URL"
echo ""
print_warning "2. Update the .env file:"
echo "   - Open $ENV_FILE"
echo "   - Replace 'your_neon_database_url_here' with your actual Neon URL"
echo "   - The URL should look like:"
echo "     postgresql://username:password@ep-example-123456-pooler.us-west-2.aws.neon.tech/database_name?sslmode=require"
echo ""
print_warning "3. Test the connection:"
echo "   - Run: cd $API_DIR && python3 -c \"from database import test_database_connection; test_database_connection()\""
echo ""
print_warning "4. Start the API server:"
echo "   - Run: ./quick_start.sh run"
echo ""

# Check if we can help with the current hardcoded URL
CURRENT_DB_URL="postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

print_status "Current hardcoded database URL found:"
echo "   $CURRENT_DB_URL"
echo ""

read -p "Do you want to use this URL in your .env file? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Update .env file with current URL
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|your_neon_database_url_here|$CURRENT_DB_URL|g" "$ENV_FILE"
    else
        # Linux
        sed -i "s|your_neon_database_url_here|$CURRENT_DB_URL|g" "$ENV_FILE"
    fi
    print_success "Updated .env file with current database URL"
    
    # Test the connection
    print_status "Testing database connection..."
    cd "$API_DIR"
    if python3 -c "from database import test_database_connection; test_database_connection()"; then
        print_success "Database connection test successful!"
    else
        print_error "Database connection test failed"
        print_warning "Please check your Neon database credentials"
    fi
    cd ..
else
    print_warning "Please manually update the DATABASE_URL in $ENV_FILE"
fi

print_status "Setup complete!"
print_warning "Remember to:"
echo "   - Never commit .env file to version control"
echo "   - Use different database URLs for development and production"
echo "   - Set up proper environment variables in your deployment platform"
echo ""
print_success "Your Neon database connection is now configured for live app testing!" 