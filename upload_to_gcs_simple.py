#!/usr/bin/env python3
"""
Simple Google Cloud Storage Upload Script
Uses gcloud credentials for authentication
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

def upload_file_to_gcs(local_file_path, bucket_name, destination_blob_name=None):
    """Upload a file using gsutil"""
    if destination_blob_name is None:
        destination_blob_name = os.path.basename(local_file_path)
    
    gcs_path = f"gs://{bucket_name}/{destination_blob_name}"
    
    print(f"Uploading {local_file_path} to {gcs_path}")
    
    success, output = run_gsutil_command(['gsutil', 'cp', local_file_path, gcs_path])
    
    if success:
        print(f"✅ Successfully uploaded {local_file_path}")
        print(f"   URL: {gcs_path}")
        return True
    else:
        print(f"❌ Error uploading file: {output}")
        return False

def upload_directory_to_gcs(local_dir_path, bucket_name, destination_prefix=""):
    """Upload a directory recursively using gsutil"""
    local_path = Path(local_dir_path)
    
    if not local_path.exists() or not local_path.is_dir():
        print(f"❌ Error: Directory {local_dir_path} does not exist or is not a directory")
        return False
    
    gcs_path = f"gs://{bucket_name}/{destination_prefix}"
    
    print(f"Uploading directory {local_dir_path} to {gcs_path}")
    
    success, output = run_gsutil_command(['gsutil', '-m', 'cp', '-r', str(local_path), gcs_path])
    
    if success:
        print(f"✅ Successfully uploaded directory {local_dir_path}")
        print(f"   URL: {gcs_path}")
        return True
    else:
        print(f"❌ Error uploading directory: {output}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload files to Google Cloud Storage using gsutil')
    parser.add_argument('source', help='Local file or directory path')
    parser.add_argument('bucket', help='GCS bucket name')
    parser.add_argument('--destination', '-d', help='Destination path in GCS (optional)')
    parser.add_argument('--recursive', '-r', action='store_true', help='Upload directory recursively')
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"❌ Error: Source path {args.source} does not exist")
        sys.exit(1)
    
    if source_path.is_file():
        success = upload_file_to_gcs(str(source_path), args.bucket, args.destination)
    elif source_path.is_dir():
        if args.recursive:
            success = upload_directory_to_gcs(str(source_path), args.bucket, args.destination)
        else:
            print("❌ Error: Use --recursive flag to upload directories")
            sys.exit(1)
    else:
        print(f"❌ Error: {args.source} is not a valid file or directory")
        sys.exit(1)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 