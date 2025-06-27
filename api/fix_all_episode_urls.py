#!/usr/bin/env python3
"""
Script to fix all episode URLs to point to the correct Google Cloud Storage URLs.
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

def get_series_folder_mapping():
    """Get mapping of series titles to folder names."""
    return {
        'Dragnet': 'dragnet',
        'Petrocelli': 'petrocelli', 
        'Longstreet': 'longstreet',
        'Commando Cody - Sky Marshal of the Universe': 'commando_cody',
        'Bonanza': 'bonanza',
        'Ghost Squad': 'ghost_squad',
        'The Count of Monte Cristo': 'count_of_monte_cristo',
        'The Lone Ranger': 'lone_ranger',
        'Man with a Camera': 'man_with_a_camera',
        'Mike Hammer': 'mike_hammer'
    }

def fix_all_episode_urls():
    """Update all episode URLs to use correct Google Cloud Storage URLs."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    try:
        print("🎬 Fixing All Episode URLs to Google Cloud Storage")
        print("=" * 60)
        
        # Get series folder mapping
        series_folders = get_series_folder_mapping()
        
        # Get all series with episodes
        cur.execute("""
            SELECT DISTINCT c.id, c.title 
            FROM content c 
            INNER JOIN episodes e ON c.id = e.series_id 
            WHERE c.type = 'SERIES'
            ORDER BY c.title
        """)
        series_list = cur.fetchall()
        
        total_updated = 0
        
        for series_id, series_title in series_list:
            print(f"\n📺 Processing series: {series_title}")
            
            # Get folder name for this series
            folder_name = series_folders.get(series_title)
            if not folder_name:
                print(f"  ⚠️  No folder mapping found for: {series_title}")
                continue
                
            # Get all episodes for this series
            cur.execute("""
                SELECT id, title, content_url, poster_url 
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number
            """, (series_id,))
            episodes = cur.fetchall()
            
            series_updated = 0
            for episode_id, episode_title, content_url, poster_url in episodes:
                # Fix content URL
                if content_url and not content_url.startswith('http'):
                    # Remove leading slash if present
                    clean_url = content_url.lstrip('/')
                    # Remove 'pecantv_series/' prefix if present
                    if clean_url.startswith('pecantv_series/'):
                        clean_url = clean_url[15:]  # Remove 'pecantv_series/'
                    
                    new_content_url = f"https://storage.googleapis.com/pecantv_series/{folder_name}/{clean_url}"
                    
                    # Fix poster URL if it exists and needs fixing
                    new_poster_url = poster_url
                    if poster_url and not poster_url.startswith('http'):
                        clean_poster_url = poster_url.lstrip('/')
                        if clean_poster_url.startswith('pecantv_series/'):
                            clean_poster_url = clean_poster_url[15:]
                        new_poster_url = f"https://storage.googleapis.com/pecantv_series/{folder_name}/{clean_poster_url}"
                    
                    # Update the episode
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, poster_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (new_content_url, new_poster_url, datetime.now(timezone.utc), episode_id))
                    
                    print(f"  ✅ Updated: {episode_title}")
                    print(f"     Content: {content_url} → {new_content_url}")
                    if poster_url != new_poster_url:
                        print(f"     Poster: {poster_url} → {new_poster_url}")
                    
                    series_updated += 1
                else:
                    print(f"  ℹ️  Skipped (already GCS URL): {episode_title}")
            
            total_updated += series_updated
            print(f"  📊 Updated {series_updated} episodes for {series_title}")
        
        conn.commit()
        print(f"\n✅ Successfully updated {total_updated} episodes across all series.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_all_episode_urls() 