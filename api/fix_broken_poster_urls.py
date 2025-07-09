#!/usr/bin/env python3
"""
Script to fix broken poster URLs by checking what files actually exist in GCS
"""

import subprocess
import re
from database import get_db
from models import Content, ContentType

def get_gcs_files():
    """Get list of all files in the GCS bucket"""
    try:
        result = subprocess.run(
            ['gsutil', 'ls', 'gs://pecantv_title_images/'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            # Extract just the filename from the full path
            filenames = [f.split('/')[-1] for f in files if f]
            return filenames
        else:
            print(f"❌ Error listing GCS files: {result.stderr}")
            return []
    except Exception as e:
        print(f"❌ Error accessing GCS: {e}")
        return []

def fix_broken_posters():
    """Fix broken poster URLs by checking what files actually exist"""
    
    print("🔍 Getting list of files in GCS bucket...")
    gcs_files = get_gcs_files()
    
    if not gcs_files:
        print("❌ Could not get GCS file list")
        return
    
    print(f"✅ Found {len(gcs_files)} files in GCS bucket")
    
    db = next(get_db())
    
    try:
        # Get all films with broken poster URLs
        films = db.query(Content).filter(Content.type == ContentType.FILM).all()
        
        fixed_count = 0
        
        for film in films:
            if not film.poster_url or film.poster_url == 'NONE':
                continue
            
            # Extract filename from current URL
            current_filename = film.poster_url.split('/')[-1]
            
            # Check if current file exists
            if current_filename in gcs_files:
                continue  # File exists, no need to fix
            
            print(f"\n🔧 Checking: {film.title}")
            print(f"  Current: {current_filename}")
            
            # Try to find a matching file with different extension
            base_name = current_filename.rsplit('.', 1)[0]  # Remove extension
            
            # Look for files with same base name but different extension
            possible_matches = []
            for gcs_file in gcs_files:
                if gcs_file.startswith(base_name + '.'):
                    possible_matches.append(gcs_file)
            
            if possible_matches:
                # Use the first match (usually .png is preferred over .jpg)
                new_filename = sorted(possible_matches)[0]
                new_url = f"https://storage.googleapis.com/pecantv_title_images/{new_filename}"
                
                print(f"  ✅ Found match: {new_filename}")
                print(f"  🔄 Updating URL...")
                
                film.poster_url = new_url
                fixed_count += 1
            else:
                print(f"  ❌ No matching file found")
        
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ Fixed {fixed_count} poster URLs")
        else:
            print(f"\n✅ No broken URLs found to fix")
            
    except Exception as e:
        print(f"❌ Error fixing posters: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_broken_posters() 