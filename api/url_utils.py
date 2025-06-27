#!/usr/bin/env python3
"""
Utility functions for normalizing and constructing GCS URLs for media fields.
"""
import re

def normalize_gcs_url(filename, folder, bucket='pecantv_series'):
    """
    Given a filename and folder, return the full GCS URL.
    Removes any leading slashes or duplicate folder names.
    """
    if not filename:
        return ''
    # Remove leading slashes
    filename = filename.lstrip('/')
    # Remove any 'pecantv_series/' prefix
    if filename.startswith(f'{bucket}/'):
        filename = filename[len(f'{bucket}/'):]
    # Remove duplicate folder (e.g., dragnet/dragnet/Dragnet1.mp4)
    pattern = rf'^{folder}/({folder}/)?'
    filename = re.sub(pattern, f'{folder}/', filename)
    return f'https://storage.googleapis.com/{bucket}/{folder}/{filename}'

# Example usage:
# url = normalize_gcs_url('dragnet/Dragnet1.mp4', 'dragnet') 