#!/usr/bin/env python3
"""
Comprehensive URL Fixer Script for PecanTV

This script standardizes all media URLs in the database to Google Cloud Storage format.
It fixes episode content URLs, trailer URLs, poster URLs, and removes duplicate folder names.

Usage:
    python scripts/fix_all_urls.py

Features:
- Fixes episode content URLs to GCS format
- Fixes trailer URLs to GCS format  
- Fixes poster URLs to GCS format
- Removes duplicate folder names in URLs
- Standardizes all URLs to consistent format
- Provides detailed logging and verification
"""

import os
import sys
import psycopg2
import re
from datetime import datetime, timezone
from typing import List, Dict, Tuple

# Add the api directory to the path so we can import url_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))
from url_utils import normalize_gcs_url

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# GCS bucket name
GCS_BUCKET = 'pecantv_series'

class URLFixer:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.stats = {
            'episodes_fixed': 0,
            'trailers_fixed': 0,
            'posters_fixed': 0,
            'duplicates_removed': 0,
            'errors': 0
        }
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**DB_PARAMS)
            self.cur = self.conn.cursor()
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("✅ Database connection closed")
    
    def get_series_folders(self) -> Dict[int, str]:
        """Get mapping of series IDs to folder names"""
        self.cur.execute("""
            SELECT id, title FROM content 
            WHERE type = 'SERIES'
            ORDER BY title
        """)
        series = {}
        for row in self.cur.fetchall():
            series_id, title = row
            # Convert title to folder name (lowercase, no spaces)
            folder = title.lower().replace(' ', '_').replace('-', '_')
            series[series_id] = folder
        return series
    
    def fix_episode_urls(self, series_folders: Dict[int, str]):
        """Fix episode content URLs"""
        print("\n🔧 Fixing episode content URLs...")
        
        self.cur.execute("""
            SELECT e.id, e.content_url, e.series_id, c.title as series_title
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE e.content_url IS NOT NULL AND e.content_url != ''
        """)
        
        episodes = self.cur.fetchall()
        print(f"Found {len(episodes)} episodes to process")
        
        for episode_id, content_url, series_id, series_title in episodes:
            try:
                if not content_url:
                    continue
                
                # Get the folder name for this series
                folder = series_folders.get(series_id)
                if not folder:
                    print(f"  ⚠️  No folder mapping for series {series_title} (ID: {series_id})")
                    continue
                
                # Extract filename from URL
                filename = self.extract_filename(content_url)
                if not filename:
                    continue
                
                # Create new GCS URL
                new_url = normalize_gcs_url(filename, folder, GCS_BUCKET)
                
                if new_url != content_url:
                    self.cur.execute(
                        "UPDATE episodes SET content_url = %s, updated_at = %s WHERE id = %s",
                        (new_url, datetime.now(timezone.utc), episode_id)
                    )
                    print(f"  ✅ Fixed episode {episode_id}: {content_url} → {new_url}")
                    self.stats['episodes_fixed'] += 1
                
            except Exception as e:
                print(f"  ❌ Error fixing episode {episode_id}: {e}")
                self.stats['errors'] += 1
        
        self.conn.commit()
        print(f"✅ Fixed {self.stats['episodes_fixed']} episode URLs")
    
    def fix_trailer_urls(self, series_folders: Dict[int, str]):
        """Fix trailer URLs in content table"""
        print("\n🎬 Fixing trailer URLs...")
        
        self.cur.execute("""
            SELECT id, title, trailer_url, type
            FROM content 
            WHERE trailer_url IS NOT NULL AND trailer_url != ''
        """)
        
        content_items = self.cur.fetchall()
        print(f"Found {len(content_items)} content items with trailer URLs")
        
        for content_id, title, trailer_url, content_type in content_items:
            try:
                if not trailer_url:
                    continue
                
                # For series, use the series folder
                if content_type == 'SERIES':
                    folder = series_folders.get(content_id)
                    if not folder:
                        # Try to derive folder from title
                        folder = title.lower().replace(' ', '_').replace('-', '_')
                else:
                    # For movies, use a general folder or derive from title
                    folder = title.lower().replace(' ', '_').replace('-', '_')
                
                # Extract filename from URL
                filename = self.extract_filename(trailer_url)
                if not filename:
                    continue
                
                # Create new GCS URL
                new_url = normalize_gcs_url(filename, folder, GCS_BUCKET)
                
                if new_url != trailer_url:
                    self.cur.execute(
                        "UPDATE content SET trailer_url = %s, updated_at = %s WHERE id = %s",
                        (new_url, datetime.now(timezone.utc), content_id)
                    )
                    print(f"  ✅ Fixed trailer for {title}: {trailer_url} → {new_url}")
                    self.stats['trailers_fixed'] += 1
                
            except Exception as e:
                print(f"  ❌ Error fixing trailer for {title}: {e}")
                self.stats['errors'] += 1
        
        self.conn.commit()
        print(f"✅ Fixed {self.stats['trailers_fixed']} trailer URLs")
    
    def fix_poster_urls(self, series_folders: Dict[int, str]):
        """Fix poster URLs in content table"""
        print("\n🖼️  Fixing poster URLs...")
        
        self.cur.execute("""
            SELECT id, title, poster_url, type
            FROM content 
            WHERE poster_url IS NOT NULL AND poster_url != ''
        """)
        
        content_items = self.cur.fetchall()
        print(f"Found {len(content_items)} content items with poster URLs")
        
        for content_id, title, poster_url, content_type in content_items:
            try:
                if not poster_url:
                    continue
                
                # For series, use the series folder
                if content_type == 'SERIES':
                    folder = series_folders.get(content_id)
                    if not folder:
                        # Try to derive folder from title
                        folder = title.lower().replace(' ', '_').replace('-', '_')
                else:
                    # For movies, use a general folder or derive from title
                    folder = title.lower().replace(' ', '_').replace('-', '_')
                
                # Extract filename from URL
                filename = self.extract_filename(poster_url)
                if not filename:
                    continue
                
                # Create new GCS URL
                new_url = normalize_gcs_url(filename, folder, GCS_BUCKET)
                
                if new_url != poster_url:
                    self.cur.execute(
                        "UPDATE content SET poster_url = %s, updated_at = %s WHERE id = %s",
                        (new_url, datetime.now(timezone.utc), content_id)
                    )
                    print(f"  ✅ Fixed poster for {title}: {poster_url} → {new_url}")
                    self.stats['posters_fixed'] += 1
                
            except Exception as e:
                print(f"  ❌ Error fixing poster for {title}: {e}")
                self.stats['errors'] += 1
        
        self.conn.commit()
        print(f"✅ Fixed {self.stats['posters_fixed']} poster URLs")
    
    def fix_episode_poster_urls(self, series_folders: Dict[int, str]):
        """Fix poster URLs in episodes table"""
        print("\n🖼️  Fixing episode poster URLs...")
        
        self.cur.execute("""
            SELECT e.id, e.poster_url, e.series_id, c.title as series_title
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE e.poster_url IS NOT NULL AND e.poster_url != ''
        """)
        
        episodes = self.cur.fetchall()
        print(f"Found {len(episodes)} episodes with poster URLs")
        
        for episode_id, poster_url, series_id, series_title in episodes:
            try:
                if not poster_url:
                    continue
                
                # Get the folder name for this series
                folder = series_folders.get(series_id)
                if not folder:
                    print(f"  ⚠️  No folder mapping for series {series_title} (ID: {series_id})")
                    continue
                
                # Extract filename from URL
                filename = self.extract_filename(poster_url)
                if not filename:
                    continue
                
                # Create new GCS URL
                new_url = normalize_gcs_url(filename, folder, GCS_BUCKET)
                
                if new_url != poster_url:
                    self.cur.execute(
                        "UPDATE episodes SET poster_url = %s, updated_at = %s WHERE id = %s",
                        (new_url, datetime.now(timezone.utc), episode_id)
                    )
                    print(f"  ✅ Fixed episode poster {episode_id}: {poster_url} → {new_url}")
                    self.stats['posters_fixed'] += 1
                
            except Exception as e:
                print(f"  ❌ Error fixing episode poster {episode_id}: {e}")
                self.stats['errors'] += 1
        
        self.conn.commit()
        print(f"✅ Fixed {self.stats['posters_fixed']} episode poster URLs")
    
    def extract_filename(self, url: str) -> str:
        """Extract filename from URL, handling various formats"""
        if not url:
            return None
        
        # Remove leading slashes
        url = url.lstrip('/')
        
        # Handle GCS URLs
        if 'storage.googleapis.com' in url:
            # Extract path after bucket name
            parts = url.split(f'{GCS_BUCKET}/')
            if len(parts) > 1:
                return parts[1]
        
        # Handle local paths
        if url.startswith('pecantv_series/'):
            return url[len('pecantv_series/'):]
        
        # Handle relative paths
        if '/' in url:
            return url
        
        # Handle just filenames
        return url
    
    def remove_duplicate_folders(self):
        """Remove duplicate folder names in URLs"""
        print("\n🔄 Removing duplicate folder names...")
        
        # Fix content table URLs
        self.cur.execute("""
            SELECT id, title, content_url, poster_url, trailer_url
            FROM content 
            WHERE content_url LIKE '%/%/%' OR poster_url LIKE '%/%/%' OR trailer_url LIKE '%/%/%'
        """)
        
        content_items = self.cur.fetchall()
        print(f"Found {len(content_items)} content items with potential duplicate folders")
        
        for content_id, title, content_url, poster_url, trailer_url in content_items:
            try:
                updated = False
                
                # Fix content_url
                if content_url and '/' in content_url:
                    new_content_url = self.remove_duplicate_folder(content_url)
                    if new_content_url != content_url:
                        self.cur.execute(
                            "UPDATE content SET content_url = %s WHERE id = %s",
                            (new_content_url, content_id)
                        )
                        print(f"  ✅ Fixed content URL for {title}: {content_url} → {new_content_url}")
                        updated = True
                
                # Fix poster_url
                if poster_url and '/' in poster_url:
                    new_poster_url = self.remove_duplicate_folder(poster_url)
                    if new_poster_url != poster_url:
                        self.cur.execute(
                            "UPDATE content SET poster_url = %s WHERE id = %s",
                            (new_poster_url, content_id)
                        )
                        print(f"  ✅ Fixed poster URL for {title}: {poster_url} → {new_poster_url}")
                        updated = True
                
                # Fix trailer_url
                if trailer_url and '/' in trailer_url:
                    new_trailer_url = self.remove_duplicate_folder(trailer_url)
                    if new_trailer_url != trailer_url:
                        self.cur.execute(
                            "UPDATE content SET trailer_url = %s WHERE id = %s",
                            (new_trailer_url, content_id)
                        )
                        print(f"  ✅ Fixed trailer URL for {title}: {trailer_url} → {new_trailer_url}")
                        updated = True
                
                if updated:
                    self.stats['duplicates_removed'] += 1
                
            except Exception as e:
                print(f"  ❌ Error fixing URLs for {title}: {e}")
                self.stats['errors'] += 1
        
        # Fix episode URLs
        self.cur.execute("""
            SELECT id, content_url, poster_url
            FROM episodes 
            WHERE content_url LIKE '%/%/%' OR poster_url LIKE '%/%/%'
        """)
        
        episodes = self.cur.fetchall()
        print(f"Found {len(episodes)} episodes with potential duplicate folders")
        
        for episode_id, content_url, poster_url in episodes:
            try:
                updated = False
                
                # Fix content_url
                if content_url and '/' in content_url:
                    new_content_url = self.remove_duplicate_folder(content_url)
                    if new_content_url != content_url:
                        self.cur.execute(
                            "UPDATE episodes SET content_url = %s WHERE id = %s",
                            (new_content_url, episode_id)
                        )
                        print(f"  ✅ Fixed episode content URL {episode_id}: {content_url} → {new_content_url}")
                        updated = True
                
                # Fix poster_url
                if poster_url and '/' in poster_url:
                    new_poster_url = self.remove_duplicate_folder(poster_url)
                    if new_poster_url != poster_url:
                        self.cur.execute(
                            "UPDATE episodes SET poster_url = %s WHERE id = %s",
                            (new_poster_url, episode_id)
                        )
                        print(f"  ✅ Fixed episode poster URL {episode_id}: {poster_url} → {new_poster_url}")
                        updated = True
                
                if updated:
                    self.stats['duplicates_removed'] += 1
                
            except Exception as e:
                print(f"  ❌ Error fixing episode URLs {episode_id}: {e}")
                self.stats['errors'] += 1
        
        self.conn.commit()
        print(f"✅ Removed duplicate folders from {self.stats['duplicates_removed']} URLs")
    
    def remove_duplicate_folder(self, url: str) -> str:
        """Remove duplicate folder names in a URL"""
        if not url or '/' not in url:
            return url
        
        # Split by '/' and remove consecutive duplicates
        parts = url.split('/')
        cleaned_parts = []
        
        for i, part in enumerate(parts):
            if i == 0 or part != parts[i-1]:
                cleaned_parts.append(part)
        
        return '/'.join(cleaned_parts)
    
    def verify_urls(self):
        """Verify that URLs are properly formatted"""
        print("\n🔍 Verifying URL formats...")
        
        # Check for URLs that don't start with GCS format
        self.cur.execute("""
            SELECT COUNT(*) FROM content 
            WHERE (content_url IS NOT NULL AND content_url != '' AND content_url NOT LIKE 'https://storage.googleapis.com/%')
               OR (poster_url IS NOT NULL AND poster_url != '' AND poster_url NOT LIKE 'https://storage.googleapis.com/%')
               OR (trailer_url IS NOT NULL AND trailer_url != '' AND trailer_url NOT LIKE 'https://storage.googleapis.com/%')
        """)
        
        content_count = self.cur.fetchone()[0]
        
        self.cur.execute("""
            SELECT COUNT(*) FROM episodes 
            WHERE (content_url IS NOT NULL AND content_url != '' AND content_url NOT LIKE 'https://storage.googleapis.com/%')
               OR (poster_url IS NOT NULL AND poster_url != '' AND poster_url NOT LIKE 'https://storage.googleapis.com/%')
        """)
        
        episode_count = self.cur.fetchone()[0]
        
        if content_count == 0 and episode_count == 0:
            print("✅ All URLs are properly formatted!")
        else:
            print(f"⚠️  Found {content_count} content items and {episode_count} episodes with non-GCS URLs")
    
    def print_stats(self):
        """Print summary statistics"""
        print("\n" + "="*50)
        print("📊 URL FIXING SUMMARY")
        print("="*50)
        print(f"Episodes fixed: {self.stats['episodes_fixed']}")
        print(f"Trailers fixed: {self.stats['trailers_fixed']}")
        print(f"Posters fixed: {self.stats['posters_fixed']}")
        print(f"Duplicate folders removed: {self.stats['duplicates_removed']}")
        print(f"Errors encountered: {self.stats['errors']}")
        print("="*50)
    
    def run(self):
        """Run the complete URL fixing process"""
        print("🚀 Starting comprehensive URL fixer...")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.connect()
            
            # Get series folder mappings
            series_folders = self.get_series_folders()
            print(f"📁 Found {len(series_folders)} series folders")
            
            # Fix all URL types
            self.fix_episode_urls(series_folders)
            self.fix_trailer_urls(series_folders)
            self.fix_poster_urls(series_folders)
            self.fix_episode_poster_urls(series_folders)
            self.remove_duplicate_folders()
            
            # Verify results
            self.verify_urls()
            
            # Print summary
            self.print_stats()
            
            print(f"\n✅ URL fixing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            self.stats['errors'] += 1
        finally:
            self.disconnect()

def main():
    """Main entry point"""
    print("🎬 PecanTV URL Fixer")
    print("=" * 50)
    
    # Check if running from correct directory
    if not os.path.exists('api/url_utils.py'):
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected: python scripts/fix_all_urls.py")
        sys.exit(1)
    
    # Run the fixer
    fixer = URLFixer()
    fixer.run()

if __name__ == "__main__":
    main() 