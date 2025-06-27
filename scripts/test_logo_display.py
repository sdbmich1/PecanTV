#!/usr/bin/env python3
"""
Script to test and verify logo display in the PecanTV iOS app.
"""

import os

def check_logo_files():
    """Check if logo files exist and are properly configured."""
    print("🔍 Checking PecanTV Logo Files...")
    print("=" * 50)
    
    # Check main logo file
    logo_path = "PecanTV/PECANTV/PECANTV/Assets.xcassets/pecantv_logo.imageset/pecantv_logo.png"
    if os.path.exists(logo_path):
        file_size = os.path.getsize(logo_path)
        print(f"✅ Logo file exists: {logo_path}")
        print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    else:
        print(f"❌ Logo file missing: {logo_path}")
    
    # Check Contents.json
    contents_path = "PecanTV/PECANTV/PECANTV/Assets.xcassets/pecantv_logo.imageset/Contents.json"
    if os.path.exists(contents_path):
        print(f"✅ Logo configuration exists: {contents_path}")
    else:
        print(f"❌ Logo configuration missing: {contents_path}")

def check_launch_screen():
    """Check launch screen configuration."""
    print("\n🚀 Checking Launch Screen...")
    print("=" * 50)
    
    launch_screen_path = "PecanTV/LaunchScreen.storyboard"
    if os.path.exists(launch_screen_path):
        print(f"✅ Launch screen exists: {launch_screen_path}")
        
        # Check if it references the logo
        with open(launch_screen_path, 'r') as f:
            content = f.read()
            if 'pecantv_logo' in content:
                print("✅ Launch screen references pecantv_logo")
            else:
                print("❌ Launch screen doesn't reference pecantv_logo")
    else:
        print(f"❌ Launch screen missing: {launch_screen_path}")

def provide_fixes():
    """Provide suggestions for fixing logo issues."""
    print("\n🔧 Logo Display Fixes:")
    print("=" * 50)
    
    print("1. **If logo doesn't appear on launch screen:**")
    print("   - Open Xcode")
    print("   - Go to LaunchScreen.storyboard")
    print("   - Make sure the ImageView references 'pecantv_logo'")
    print("   - Set background color to black")
    
    print("\n2. **If logo doesn't appear on splash screen:**")
    print("   - Check that pecantv_logo.png exists in Assets.xcassets")
    print("   - Verify the image name matches exactly: 'pecantv_logo'")
    print("   - Clean and rebuild the project in Xcode")
    
    print("\n3. **To test the logo:**")
    print("   - Build and run the app in Xcode")
    print("   - Watch the launch screen and splash screen")
    print("   - Check both light and dark mode")

def main():
    """Main function to run all logo checks."""
    print("🎬 PecanTV Logo Display Test")
    print("=" * 50)
    
    check_logo_files()
    check_launch_screen()
    provide_fixes()
    
    print("\n✅ Logo test complete!")
    print("\nNext steps:")
    print("1. Open the project in Xcode")
    print("2. Clean build folder (Product > Clean Build Folder)")
    print("3. Build and run on device/simulator")
    print("4. Watch for the logo on launch and splash screens")

if __name__ == "__main__":
    main() 