#!/usr/bin/env python3
"""
Fix episode poster URLs to match their series poster URLs
"""

import psycopg2

# Database connection
DB_CONFIG = {
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'sslmode': 'require'
}

def fix_episode_posters():
    """Update episode poster URLs to match their series poster URLs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all episodes with their series poster URLs
        cursor.execute("""
            SELECT e.id, e.title, e.poster_url, c.title as series_title, c.poster_url as series_poster_url
            FROM episodes e 
            JOIN content c ON e.series_id = c.id 
            WHERE e.poster_url != c.poster_url
        """)
        
        episodes_to_update = cursor.fetchall()
        
        updated_count = 0
        
        for episode_id, episode_title, episode_poster, series_title, series_poster in episodes_to_update:
            # Update the episode poster URL to match the series
            cursor.execute("""
                UPDATE episodes 
                SET poster_url = %s
                WHERE id = %s
            """, (series_poster, episode_id))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated {episode_title} ({series_title}) poster URL")
        
        conn.commit()
        print(f"🎉 Successfully updated {updated_count} episode poster URLs")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main function"""
    print("🔧 Fixing episode poster URLs...")
    fix_episode_posters()
    print("✅ Episode poster URL fix complete!")

if __name__ == "__main__":
    main() 