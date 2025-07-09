#!/usr/bin/env python3
"""
Fix Malformed Image URLs in PecanTV Database
Fixes URLs that have double URL paths like:
https://storage.googleapis.com/pecantv_series/folder/https://storage.googleapis.com/pecantv_title_images/image.png
"""

import sqlite3
import re
from datetime import datetime, timezone
import os

def connect_to_database():
    """Connect to the SQLite database"""
    db_path = "database/pecantv.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def fix_malformed_urls():
    """Fix malformed URLs in the database"""
    conn = connect_to_database()
    if not conn:
        return
    
    cur = conn.cursor()
    
    print("🔧 Fixing malformed image URLs...")
    
    # Find episodes with malformed poster URLs
    cur.execute("""
        SELECT id, title, poster_url, series_id
        FROM episodes 
        WHERE poster_url LIKE '%https://%https://%'
        OR poster_url LIKE '%http://%http://%'
    """)
    
    malformed_episodes = cur.fetchall()
    print(f"Found {len(malformed_episodes)} episodes with malformed URLs")
    
    fixed_count = 0
    
    for episode in malformed_episodes:
        old_url = episode['poster_url']
        new_url = extract_correct_url(old_url)
        
        if new_url and new_url != old_url:
            cur.execute("""
                UPDATE episodes 
                SET poster_url = ?, updated_at = ?
                WHERE id = ?
            """, (new_url, datetime.now(timezone.utc), episode['id']))
            
            print(f"✅ Fixed: {episode['title']}")
            print(f"  Old: {old_url}")
            print(f"  New: {new_url}")
            print()
            
            fixed_count += 1
    
    # Also check content table
    cur.execute("""
        SELECT id, title, poster_url
        FROM content 
        WHERE poster_url LIKE '%https://%https://%'
        OR poster_url LIKE '%http://%http://%'
    """)
    
    malformed_content = cur.fetchall()
    print(f"Found {len(malformed_content)} content items with malformed URLs")
    
    for content in malformed_content:
        old_url = content['poster_url']
        new_url = extract_correct_url(old_url)
        
        if new_url and new_url != old_url:
            cur.execute("""
                UPDATE content 
                SET poster_url = ?, updated_at = ?
                WHERE id = ?
            """, (new_url, datetime.now(timezone.utc), content['id']))
            
            print(f"✅ Fixed: {content['title']}")
            print(f"  Old: {old_url}")
            print(f"  New: {new_url}")
            print()
            
            fixed_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"🎉 Fixed {fixed_count} malformed URLs!")

def extract_correct_url(malformed_url):
    """Extract the correct URL from a malformed URL"""
    if not malformed_url:
        return None
    
    # Pattern to find URLs within URLs
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, malformed_url)
    
    if len(urls) >= 2:
        # Take the last URL (usually the correct one)
        correct_url = urls[-1]
        
        # Clean up any trailing characters
        correct_url = correct_url.rstrip('/')
        
        return correct_url
    
    return malformed_url

def verify_fixes():
    """Verify that the fixes worked"""
    conn = connect_to_database()
    if not conn:
        return
    
    cur = conn.cursor()
    
    print("\n🔍 Verifying fixes...")
    
    # Check for remaining malformed URLs
    cur.execute("""
        SELECT COUNT(*) as count
        FROM episodes 
        WHERE poster_url LIKE '%https://%https://%'
        OR poster_url LIKE '%http://%http://%'
    """)
    
    remaining_episodes = cur.fetchone()['count']
    
    cur.execute("""
        SELECT COUNT(*) as count
        FROM content 
        WHERE poster_url LIKE '%https://%https://%'
        OR poster_url LIKE '%http://%http://%'
    """)
    
    remaining_content = cur.fetchone()['count']
    
    print(f"Remaining malformed URLs:")
    print(f"  Episodes: {remaining_episodes}")
    print(f"  Content: {remaining_content}")
    
    if remaining_episodes == 0 and remaining_content == 0:
        print("✅ All malformed URLs have been fixed!")
    else:
        print("⚠️  Some malformed URLs remain")
    
    conn.close()

def test_sample_urls():
    """Test a few sample URLs to make sure they work"""
    conn = connect_to_database()
    if not conn:
        return
    
    cur = conn.cursor()
    
    print("\n🧪 Testing sample URLs...")
    
    # Get a few sample URLs
    cur.execute("""
        SELECT poster_url, title
        FROM episodes 
        WHERE poster_url IS NOT NULL AND poster_url != ''
        LIMIT 5
    """)
    
    samples = cur.fetchall()
    
    for sample in samples:
        url = sample['poster_url']
        title = sample['title']
        
        print(f"  Testing: {title}")
        print(f"    URL: {url}")
        
        # Basic URL validation
        if url.startswith('http'):
            print("    ✅ Valid HTTP URL")
        else:
            print("    ❌ Invalid URL format")
    
    conn.close()

def main():
    """Main function"""
    print("🔧 PecanTV Malformed URL Fixer")
    print("=" * 40)
    
    # Fix malformed URLs
    fix_malformed_urls()
    
    # Verify fixes
    verify_fixes()
    
    # Test sample URLs
    test_sample_urls()
    
    print("\n🎉 URL fixing complete!")

if __name__ == "__main__":
    main() 