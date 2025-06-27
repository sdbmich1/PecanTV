#!/usr/bin/env python3
"""
Script to fix series mapping by properly grouping episodes under correct main series.
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

def fix_series_mapping():
    """Fix series mapping by properly grouping episodes under correct main series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Fixing Series Mapping")
        print("=" * 50)
        
        # Define the correct series mappings
        series_mappings = {
            # Main series ID -> Series name for URL mapping
            68: 'dragnet',           # Dragnet
            62: 'ghost_squad',       # Ghost Squad  
            21: 'petrocelli',        # Petrocelli
            78: 'bonanza',           # Bonanza
            699: 'commando_cody___sky_marshal_of_the_universe',  # Commando Cody
            691: 'lone_ranger',      # Lone Ranger
            49: 'longstreet',        # Longstreet
            700: 'man_with_a_camera', # Man with a Camera
            45: 'mike_hammer',       # Mike Hammer
            72: 'the_count_of_monte_cristo',  # The Count of Monte Cristo
            704: 'zorro\'s_black_whip'  # Zorro's Black Whip
        }
        
        # Update episode URLs to use correct series folders
        print("\n📺 Updating Episode URLs...")
        updates = 0
        
        for series_id, series_folder in series_mappings.items():
            print(f"\n  🔄 Processing {series_folder} (ID: {series_id})...")
            
            # Get episodes for this series
            cur.execute("""
                SELECT e.id, e.title, e.content_url, e.poster_url
                FROM episodes e
                WHERE e.series_id = %s
                ORDER BY e.episode_number
            """, (series_id,))
            
            episodes = cur.fetchall()
            
            for episode in episodes:
                old_content_url = episode['content_url']
                old_poster_url = episode['poster_url']
                
                # Fix content URL
                new_content_url = old_content_url
                if old_content_url and 'pecantv_series' in old_content_url:
                    # Extract filename from URL
                    filename = old_content_url.split('/')[-1]
                    new_content_url = f"https://storage.googleapis.com/pecantv_series/{series_folder}/{filename}"
                
                # Fix poster URL
                new_poster_url = old_poster_url
                if old_poster_url and 'pecantv_series' in old_poster_url:
                    # Extract filename from URL
                    filename = old_poster_url.split('/')[-1]
                    new_poster_url = f"https://storage.googleapis.com/pecantv_series/{series_folder}/{filename}"
                
                # Update if URLs changed
                if new_content_url != old_content_url or new_poster_url != old_poster_url:
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, poster_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode['id']))
                    
                    print(f"    ✅ {episode['title']}")
                    print(f"       Content: {old_content_url.split('/')[-2]} → {series_folder}")
                    updates += 1
        
        conn.commit()
        print(f"\n✅ Updated {updates} episodes")
        
        # Clean up individual episode series that should be deleted
        print("\n🧹 Cleaning up individual episode series...")
        
        # Get all series that are actually individual episodes
        cur.execute("""
            SELECT id, title FROM content 
            WHERE type = 'SERIES' 
            AND id NOT IN (68, 62, 21, 78, 699, 691, 49, 700, 45, 72, 704)
            AND title NOT LIKE '%Commando Cody%'
            AND title NOT LIKE '%Lone Ranger%'
            AND title NOT LIKE '%Longstreet%'
            AND title NOT LIKE '%Petrocelli%'
            AND title NOT LIKE '%Bonanza%'
            AND title NOT LIKE '%Dragnet%'
            AND title NOT LIKE '%Ghost Squad%'
            AND title NOT LIKE '%Man with a Camera%'
            AND title NOT LIKE '%Mike Hammer%'
            AND title NOT LIKE '%Count of Monte Cristo%'
            AND title NOT LIKE '%Zorro%'
        """)
        
        individual_episodes = cur.fetchall()
        print(f"  Found {len(individual_episodes)} individual episode series to clean up")
        
        # For now, just mark them as not series (we can delete later if needed)
        for episode in individual_episodes:
            print(f"    ⚠️  {episode['title']} (ID: {episode['id']}) - should be episode, not series")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_series_mapping() 