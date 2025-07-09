#!/usr/bin/env python3
"""
Upload Images to Google Cloud Storage
Specialized script for uploading images to pecantv_title_images folder
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

def run_gsutil_command(args):
    """Run gsutil command and return result"""
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def upload_image_to_gcs(local_file_path, destination_name=None):
    """Upload an image to pecantv_title_images folder"""
    if destination_name is None:
        destination_name = os.path.basename(local_file_path)
    
    gcs_path = f"gs://pecantv_series/pecantv_title_images/{destination_name}"
    
    print(f"Uploading {local_file_path} to {gcs_path}")
    
    # Determine content type based on file extension
    ext = os.path.splitext(local_file_path)[1].lower()
    content_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    }
    
    content_type = content_type_map.get(ext, 'image/jpeg')
    
    # Upload with content type
    success, output = run_gsutil_command([
        'gsutil', 'cp', '-h', f'Content-Type:{content_type}', 
        local_file_path, gcs_path
    ])
    
    if success:
        print(f"✅ Successfully uploaded {local_file_path}")
        return True
    else:
        print(f"❌ Failed to upload {local_file_path}: {output}")
        return False

def upload_folder_to_gcs(local_folder_path):
    """Upload an entire folder of images"""
    folder_name = os.path.basename(local_folder_path)
    gcs_path = f"gs://pecantv_series/pecantv_title_images/{folder_name}/"
    
    print(f"Uploading folder {local_folder_path} to {gcs_path}")
    
    success, output = run_gsutil_command([
        'gsutil', '-m', 'cp', '-r', local_folder_path, gcs_path
    ])
    
    if success:
        print(f"✅ Successfully uploaded folder {local_folder_path}")
        return True
    else:
        print(f"❌ Failed to upload folder {local_folder_path}: {output}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload images to pecantv_title_images folder')
    parser.add_argument('path', help='Path to image file or folder')
    parser.add_argument('--destination', '-d', help='Destination filename in GCS (optional)')
    parser.add_argument('--folder', '-f', action='store_true', help='Upload as folder (recursive)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"❌ Error: Path {args.path} does not exist")
        sys.exit(1)
    
    if args.folder or os.path.isdir(args.path):
        upload_folder_to_gcs(args.path)
    else:
        upload_image_to_gcs(args.path, args.destination)

if __name__ == "__main__":
    main() 