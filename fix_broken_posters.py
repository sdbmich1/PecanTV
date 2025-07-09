#!/usr/bin/env python3
import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def test_url(url):
    """Test if a URL is accessible"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def find_working_fallback():
    """Find a working poster URL to use as fallback"""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    cur.execute("""
        SELECT poster_url FROM content 
        WHERE poster_url LIKE '%storage.googleapis.com%' 
        AND poster_url IS NOT NULL 
        AND poster_url != ''
        LIMIT 20
    """)
    
    urls = cur.fetchall()
    cur.close()
    conn.close()
    
    for url_tuple in urls:
        url = url_tuple[0]
        if test_url(url):
            print(f"✅ Found working fallback: {url}")
            return url
    
    print("❌ No working fallback URL found")
    return None

def fix_broken_posters(fallback_url):
    """Replace broken poster URLs with fallback"""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Get all content with poster URLs
    cur.execute("""
        SELECT id, title, poster_url FROM content 
        WHERE poster_url IS NOT NULL 
        AND poster_url != '' 
        AND poster_url NOT LIKE '%default_poster%'
        ORDER BY id
    """)
    
    content = cur.fetchall()
    
    broken_count = 0
    fixed_count = 0
    
    for item in content:
        item_id, title, poster_url = item
        
        if not test_url(poster_url):
            print(f"❌ Broken: {title} - {poster_url}")
            broken_count += 1
            
            # Update with fallback
            cur.execute("""
                UPDATE content 
                SET poster_url = %s 
                WHERE id = %s
            """, (fallback_url, item_id))
            fixed_count += 1
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n📊 Summary:")
    print(f"   Broken URLs found: {broken_count}")
    print(f"   Fixed with fallback: {fixed_count}")

if __name__ == "__main__":
    print("🔍 Finding working fallback URL...")
    fallback_url = find_working_fallback()
    
    if fallback_url:
        print(f"\n🔧 Fixing broken poster URLs...")
        fix_broken_posters(fallback_url)
    else:
        print("❌ Cannot proceed without working fallback URL") 