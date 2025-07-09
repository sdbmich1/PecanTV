#!/usr/bin/env python3
"""
Google Cloud Storage Upload Script
Upload files from your Mac to Google Cloud Storage
"""

import os
import sys
from pathlib import Path
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import argparse

def upload_file_to_gcs(local_file_path, bucket_name, destination_blob_name=None, content_type=None):
    """Upload a file to Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        if destination_blob_name is None:
            destination_blob_name = os.path.basename(local_file_path)
        
        blob = bucket.blob(destination_blob_name)
        
        if content_type:
            blob.content_type = content_type
        
        print(f"Uploading {local_file_path} to gs://{bucket_name}/{destination_blob_name}")
        blob.upload_from_filename(local_file_path)
        
        print(f"✅ Successfully uploaded {local_file_path}")
        print(f"   URL: gs://{bucket_name}/{destination_blob_name}")
        return True
        
    except DefaultCredentialsError:
        print("❌ Error: No credentials found. Please authenticate with Google Cloud:")
        print("   gcloud auth application-default login")
        return False
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return False

def upload_directory_to_gcs(local_dir_path, bucket_name, destination_prefix=""):
    """Upload a directory recursively to Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        local_path = Path(local_dir_path)
        
        if not local_path.exists() or not local_path.is_dir():
            print(f"❌ Error: Directory {local_dir_path} does not exist or is not a directory")
            return False
        
        uploaded_count = 0
        failed_count = 0
        
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                destination_blob_name = f"{destination_prefix}/{relative_path}" if destination_prefix else str(relative_path)
                
                content_type = None
                if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
                    content_type = 'video/mp4'
                elif file_path.suffix.lower() in ['.jpg', '.jpeg']:
                    content_type = 'image/jpeg'
                elif file_path.suffix.lower() in ['.png']:
                    content_type = 'image/png'
                
                if upload_file_to_gcs(str(file_path), bucket_name, destination_blob_name, content_type):
                    uploaded_count += 1
                else:
                    failed_count += 1
        
        print(f"\n📊 Upload Summary:")
        print(f"   ✅ Successfully uploaded: {uploaded_count} files")
        print(f"   ❌ Failed uploads: {failed_count} files")
        
        return failed_count == 0
        
    except DefaultCredentialsError:
        print("❌ Error: No credentials found. Please authenticate with Google Cloud:")
        print("   gcloud auth application-default login")
        return False
    except Exception as e:
        print(f"❌ Error uploading directory: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload files to Google Cloud Storage')
    parser.add_argument('source', help='Local file or directory path')
    parser.add_argument('bucket', help='GCS bucket name')
    parser.add_argument('--destination', '-d', help='Destination path in GCS (optional)')
    parser.add_argument('--content-type', '-t', help='Content type/MIME type (optional)')
    parser.add_argument('--recursive', '-r', action='store_true', help='Upload directory recursively')
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    
    if not source_path.exists():
        print(f"❌ Error: Source path {args.source} does not exist")
        sys.exit(1)
    
    if source_path.is_file():
        success = upload_file_to_gcs(str(source_path), args.bucket, args.destination, args.content_type)
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