#!/usr/bin/env python3
"""
Script to create a white placeholder image for missing posters
"""

from PIL import Image
import os

def create_white_placeholder():
    """Create a white placeholder image"""
    
    # Create a white image (300x450 is a common poster ratio)
    width, height = 300, 450
    white_image = Image.new('RGB', (width, height), color='white')
    
    # Save to pecantv_series directory
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pecantv_series")
    placeholder_path = os.path.join(static_path, "white_placeholder.jpg")
    
    white_image.save(placeholder_path, 'JPEG', quality=90)
    print(f"✅ Created white placeholder: {placeholder_path}")
    print(f"   Size: {width}x{height} pixels")
    
    return placeholder_path

if __name__ == "__main__":
    create_white_placeholder() 