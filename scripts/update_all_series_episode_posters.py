#!/usr/bin/env python3
"""
Script to update all series episodes to use their series poster image.
This will make all episodes in a series use the same poster image.
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

def update_all_series_episode_posters():
    """Update all series episodes to use their series poster image."""
    print("🎬 Updating all series episodes to use series poster images")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get all series with their poster URLs
        cur.execute("""
            SELECT c.id, c.title, c.poster_url 
            FROM content c 
            WHERE c.type = 'SERIES' 
            AND c.poster_url IS NOT NULL
            ORDER BY c.title
        """)
        
        series_data = cur.fetchall()
        print(f"Found {len(series_data)} series with poster URLs")
        print()
        
        total_episodes_updated = 0
        
        for series_id, series_title, series_poster_url in series_data:
            if not series_poster_url:
                print(f"⚠️  Skipping {series_title} - no poster URL")
                continue
                
            print(f"📺 Processing: {series_title}")
            print(f"   Series Poster: {series_poster_url}")
            
            # Get all episodes for this series
            cur.execute("""
                SELECT id, title, episode_number, poster_url 
                FROM episodes 
                WHERE series_id = %s 
                ORDER BY episode_number
            """, (series_id,))
            
            episodes = cur.fetchall()
            
            if not episodes:
                print(f"   ⚠️  No episodes found for {series_title}")
                print()
                continue
            
            episodes_updated = 0
            
            for episode_id, episode_title, episode_number, current_poster_url in episodes:
                # Skip if already using series poster
                if current_poster_url == series_poster_url:
                    print(f"   ✅ Episode {episode_number}: Already using series poster")
                    continue
                
                # Update episode to use series poster
                cur.execute("""
                    UPDATE episodes 
                    SET poster_url = %s, updated_at = %s
                    WHERE id = %s
                """, (series_poster_url, datetime.now(timezone.utc), episode_id))
                
                episodes_updated += 1
                print(f"   🔄 Episode {episode_number}: Updated to use series poster")
            
            if episodes_updated > 0:
                conn.commit()
                total_episodes_updated += episodes_updated
                print(f"   ✅ Updated {episodes_updated} episodes for {series_title}")
            else:
                print(f"   ℹ️  No updates needed for {series_title}")
            
            print()
        
        print("=" * 60)
        print(f"🎉 Complete! Updated {total_episodes_updated} episodes across {len(series_data)} series")
        print("All episodes now use their series poster image")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_all_series_episode_posters() 