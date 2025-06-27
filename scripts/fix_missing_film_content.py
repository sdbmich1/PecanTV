#!/usr/bin/env python3
"""
Script to fix films that have trailer URLs but missing content URLs.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_missing_film_content():
    """Fix films that have trailer URLs but missing content URLs."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing Films with Missing Content URLs")
        print("=" * 50)
        
        # Find films with trailer URLs but no content URLs
        cur.execute("""
            SELECT id, title, trailer_url, content_url, type
            FROM content 
            WHERE type = 'FILM' 
            AND trailer_url IS NOT NULL 
            AND trailer_url != ''
            AND (content_url IS NULL OR content_url = '')
            ORDER BY title
        """)
        
        films = cur.fetchall()
        print(f"Found {len(films)} films with missing content URLs")
        
        if not films:
            print("✅ No films need fixing!")
            return
        
        # Film content URL mappings based on trailer URLs
        film_content_mappings = {
            'Cosmos': 'https://storage.googleapis.com/pecantv_features/Cosmos_2p-1080-24fps-wCredits.mp4',
            'Creature': 'https://storage.googleapis.com/pecantv_features/Creature_2p-1080-24fps-wCredits.mp4',
            'Hercules': 'https://storage.googleapis.com/pecantv_features/Hercules_2p-1080-24fps-wCredits.mp4',
            'Hercules Against the Moon Men': 'https://storage.googleapis.com/pecantv_features/Hercules-Against-the-Moon-Men_2p-1080-24fps-wCredits.mp4',
            'Dick Tracy vs Cueball': 'https://storage.googleapis.com/pecantv_features/Dick-Tracy-vs-Cueball_2p-1080-credit-role.mp4'
        }
        
        updated = 0
        for film in films:
            print(f"\n🎬 {film['title']}")
            print(f"  🎥 Trailer URL: {film['trailer_url']}")
            print(f"  📹 Content URL: {film['content_url'] or 'MISSING'}")
            
            # Try to find content URL mapping
            content_url = None
            for title_key, url in film_content_mappings.items():
                if title_key.lower() in film['title'].lower():
                    content_url = url
                    break
            
            if content_url:
                cur.execute("""
                    UPDATE content 
                    SET content_url = %s, updated_at = %s
                    WHERE id = %s
                """, (content_url, datetime.now(timezone.utc), film['id']))
                
                print(f"  ✅ Added content URL: {content_url}")
                updated += 1
            else:
                print(f"  ⚠️  No content URL mapping found for: {film['title']}")
        
        conn.commit()
        print(f"\n✅ Updated {updated} films with content URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_missing_film_content() 