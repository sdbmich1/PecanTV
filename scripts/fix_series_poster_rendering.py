#!/usr/bin/env python3
"""
Script to fix series poster rendering by updating series that use default_poster.jpg
to use proper title images that will render in the hot series carousel.
"""

import psycopg2
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

def fix_series_poster_rendering():
    """Fix series poster rendering by updating default poster URLs."""
    print("🎨 Fixing series poster rendering")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get all series using default poster
        cur.execute("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE type = 'SERIES' 
            AND poster_url LIKE '%default_poster.jpg'
            ORDER BY title
        """)
        
        series_with_default = cur.fetchall()
        print(f"Found {len(series_with_default)} series using default poster:")
        
        for series_id, title, current_poster in series_with_default:
            print(f"  {title} (ID: {series_id})")
            print(f"    Current: {current_poster}")
        
        print()
        
        # Define new poster URLs for each series
        poster_updates = {
            'Longstreet': 'https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png',
            'Bonanza': 'https://storage.googleapis.com/pecantv_title_images/Bonanza_title-img.png',
            'Ghost Squad': 'https://storage.googleapis.com/pecantv_title_images/GhostSquad_title-img.png',
            'Man with a Camera': 'https://storage.googleapis.com/pecantv_title_images/Man-with-a-Camera_title-img.png'
        }
        
        # Update series posters
        updates_made = 0
        for series_title, new_poster_url in poster_updates.items():
            cur.execute("""
                UPDATE content 
                SET poster_url = %s, updated_at = %s
                WHERE title ILIKE %s AND type = 'SERIES'
            """, (new_poster_url, datetime.now(timezone.utc), f'%{series_title}%'))
            
            if cur.rowcount > 0:
                print(f"✅ Updated {series_title} poster to: {new_poster_url}")
                updates_made += 1
            else:
                print(f"⚠️  No match found for {series_title}")
        
        if updates_made > 0:
            conn.commit()
            print(f"\n🎉 Updated {updates_made} series posters")
            
            # Now update all episodes to use the new series posters
            print("\n🔄 Updating episode posters to match new series posters...")
            
            for series_title, new_poster_url in poster_updates.items():
                # Get series ID
                cur.execute("""
                    SELECT id FROM content 
                    WHERE title ILIKE %s AND type = 'SERIES'
                """, (f'%{series_title}%',))
                
                series_result = cur.fetchone()
                if series_result:
                    series_id = series_result[0]
                    
                    # Update all episodes for this series
                    cur.execute("""
                        UPDATE episodes 
                        SET poster_url = %s, updated_at = %s
                        WHERE series_id = %s
                    """, (new_poster_url, datetime.now(timezone.utc), series_id))
                    
                    episodes_updated = cur.rowcount
                    print(f"  Updated {episodes_updated} episodes for {series_title}")
            
            conn.commit()
            print("✅ All episode posters updated to match new series posters")
        else:
            print("ℹ️  No updates were made")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_series_poster_rendering() 