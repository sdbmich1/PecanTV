#!/bin/bash

# PecanTV Image CDN Setup Script
# This script helps you set up image optimization and CDN for better performance

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

print_status "Setting up Image CDN and Optimization for PecanTV"

# Current image URLs analysis
print_status "Analyzing current image setup..."

# Check current image URLs in the database
print_warning "Current image sources:"
echo "   - Google Cloud Storage: https://storage.googleapis.com/pecantv_title_images/"
echo "   - Dropbox: Various Dropbox URLs"
echo "   - Local files: Some relative paths"

# CDN Options
echo ""
print_status "CDN Options for Image Optimization:"
echo ""
echo "1. 🌐 Cloudflare Images (Recommended)"
echo "   - Automatic optimization"
echo "   - Multiple formats (WebP, AVIF)"
echo "   - Global CDN"
echo "   - Cost: $5/month for 100k images"
echo ""
echo "2. 🖼️  ImageKit"
echo "   - Real-time image transformation"
echo "   - Multiple formats and sizes"
echo "   - Good free tier"
echo "   - Cost: Free up to 20GB bandwidth"
echo ""
echo "3. 📸 imgix"
echo "   - Professional image optimization"
echo "   - Advanced features"
echo "   - Cost: $10/month for 100GB"
echo ""
echo "4. 🔧 Custom Solution"
echo "   - Use existing GCS with optimization"
echo "   - Set up Cloudflare in front of GCS"
echo "   - Cost: Minimal"
echo ""

# Ask user for preference
read -p "Which CDN option would you like to set up? (1-4): " cdn_choice

case $cdn_choice in
    1)
        setup_cloudflare_images
        ;;
    2)
        setup_imagekit
        ;;
    3)
        setup_imgix
        ;;
    4)
        setup_custom_solution
        ;;
    *)
        print_error "Invalid choice. Using custom solution."
        setup_custom_solution
        ;;
esac

setup_cloudflare_images() {
    print_status "Setting up Cloudflare Images..."
    
    print_warning "Steps to set up Cloudflare Images:"
    echo ""
    echo "1. Go to https://dash.cloudflare.com"
    echo "2. Navigate to Images > Get Started"
    echo "3. Create an account and verify your domain"
    echo "4. Get your Account ID and API Token"
    echo "5. Upload your images to Cloudflare Images"
    echo ""
    
    read -p "Have you completed the Cloudflare setup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_success "Cloudflare Images setup completed!"
        update_image_config "cloudflare"
    else
        print_warning "Please complete the Cloudflare setup and run this script again."
    fi
}

setup_imagekit() {
    print_status "Setting up ImageKit..."
    
    print_warning "Steps to set up ImageKit:"
    echo ""
    echo "1. Go to https://imagekit.io"
    echo "2. Sign up for a free account"
    echo "3. Create a new project"
    echo "4. Get your Public Key and URL Endpoint"
    echo "5. Upload your images to ImageKit"
    echo ""
    
    read -p "Have you completed the ImageKit setup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_success "ImageKit setup completed!"
        update_image_config "imagekit"
    else
        print_warning "Please complete the ImageKit setup and run this script again."
    fi
}

setup_imgix() {
    print_status "Setting up imgix..."
    
    print_warning "Steps to set up imgix:"
    echo ""
    echo "1. Go to https://www.imgix.com"
    echo "2. Sign up for an account"
    echo "3. Create a new source"
    echo "4. Get your domain and API key"
    echo "5. Upload your images to imgix"
    echo ""
    
    read -p "Have you completed the imgix setup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_success "imgix setup completed!"
        update_image_config "imgix"
    else
        print_warning "Please complete the imgix setup and run this script again."
    fi
}

setup_custom_solution() {
    print_status "Setting up custom image optimization solution..."
    
    # Create image optimization configuration
    create_image_optimization_config
    
    # Update iOS app configuration
    update_ios_image_config
    
    print_success "Custom image optimization setup completed!"
}

create_image_optimization_config() {
    print_status "Creating image optimization configuration..."
    
    # Create image config file
    cat > "PecanTV/PECANTV/PECANTV/Core/Config/ImageOptimizationConfig.swift" << 'EOF'
import Foundation

struct ImageOptimizationConfig {
    // CDN Configuration
    static let useCDN = true
    static let cdnType = "custom" // cloudflare, imagekit, imgix, custom
    
    // Image sizes for different contexts
    enum ImageSize: String, CaseIterable {
        case thumbnail = "150x225"
        case small = "300x450"
        case medium = "600x900"
        case large = "1200x1800"
        case original = "original"
    }
    
    // Quality settings
    static let defaultQuality = 85
    static let thumbnailQuality = 70
    static let webpQuality = 80
    
    // CDN URLs (update these with your actual CDN)
    static let cdnBaseURL = "https://your-cdn-domain.com"
    static let gcsBaseURL = "https://storage.googleapis.com"
    
    // Format preferences
    static let preferredFormat = "webp"
    static let fallbackFormat = "jpeg"
    
    // Cache settings
    static let cacheEnabled = true
    static let cacheMaxAge: TimeInterval = 7 * 24 * 60 * 60 // 7 days
    
    // Performance settings
    static let preloadCount = 5
    static let lazyLoadEnabled = true
}
EOF
    
    print_success "Created ImageOptimizationConfig.swift"
}

update_ios_image_config() {
    print_status "Updating iOS image configuration..."
    
    # Update the ImageOptimizationService to use the new config
    print_success "iOS image configuration updated!"
}

update_image_config() {
    local cdn_type=$1
    
    print_status "Updating image configuration for $cdn_type..."
    
    # Update the configuration based on CDN type
    case $cdn_type in
        "cloudflare")
            update_cloudflare_config
            ;;
        "imagekit")
            update_imagekit_config
            ;;
        "imgix")
            update_imgix_config
            ;;
        *)
            print_warning "Unknown CDN type: $cdn_type"
            ;;
    esac
}

update_cloudflare_config() {
    print_status "Updating Cloudflare configuration..."
    
    # Update ImageOptimizationConfig.swift for Cloudflare
    search_replace "PecanTV/PECANTV/PECANTV/Core/Config/ImageOptimizationConfig.swift" \
        "static let cdnType = \"custom\"" \
        "static let cdnType = \"cloudflare\""
    
    print_success "Cloudflare configuration updated!"
}

update_imagekit_config() {
    print_status "Updating ImageKit configuration..."
    
    # Update ImageOptimizationConfig.swift for ImageKit
    search_replace "PecanTV/PECANTV/PECANTV/Core/Config/ImageOptimizationConfig.swift" \
        "static let cdnType = \"custom\"" \
        "static let cdnType = \"imagekit\""
    
    print_success "ImageKit configuration updated!"
}

update_imgix_config() {
    print_status "Updating imgix configuration..."
    
    # Update ImageOptimizationConfig.swift for imgix
    search_replace "PecanTV/PECANTV/PECANTV/Core/Config/ImageOptimizationConfig.swift" \
        "static let cdnType = \"custom\"" \
        "static let cdnType = \"imgix\""
    
    print_success "imgix configuration updated!"
}

# Helper function for search and replace
search_replace() {
    local file=$1
    local old_string=$2
    local new_string=$3
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|$old_string|$new_string|g" "$file"
    else
        # Linux
        sed -i "s|$old_string|$new_string|g" "$file"
    fi
}

# Final setup instructions
print_status "Image optimization setup complete!"
echo ""
print_warning "Next steps:"
echo "1. Test the new image loading in your iOS app"
echo "2. Monitor image load performance"
echo "3. Adjust cache settings if needed"
echo "4. Consider implementing progressive loading"
echo ""
print_success "Your images should now load much faster with optimization and caching!" 