#!/usr/bin/env python3
"""
Script to verify the current status of Longstreet series in the database.
This script will show:
1. Main series information
2. All episodes in the content table
3. All episodes in the episodes table
4. Content URLs and metadata
"""

import psycopg2

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def verify_longstreet_status():
    """Verify the current status of Longstreet series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Longstreet Series Status Verification")
        print("=" * 60)
        
        # Get main series
        cur.execute("""
            SELECT id, uuid, title, type, series_name, episode_number, season_number,
                   description, content_url, poster_url, runtime, genre_id, rating_id,
                   created_at, updated_at
            FROM content 
            WHERE title = 'Longstreet' AND type = 'SERIES'
        """)
        series = cur.fetchone()
        
        if series:
            print("📺 Main Series Record:")
            print(f"   ID: {series[0]}")
            print(f"   UUID: {series[1]}")
            print(f"   Title: {series[2]}")
            print(f"   Type: {series[3]}")
            print(f"   Series Name: {series[4]}")
            print(f"   Episode: {series[5]}")
            print(f"   Season: {series[6]}")
            print(f"   Description: {series[7][:100]}..." if series[7] else "No description")
            print(f"   Content URL: {series[8] or 'None'}")
            print(f"   Poster URL: {series[9] or 'None'}")
            print(f"   Runtime: {series[10]} minutes")
            print(f"   Genre ID: {series[11]}")
            print(f"   Rating ID: {series[12]}")
            print(f"   Created: {series[13]}")
            print(f"   Updated: {series[14]}")
        else:
            print("❌ Main series record not found")
            return
        
        print("\n" + "=" * 60)
        
        # Get all episodes from content table
        cur.execute("""
            SELECT id, uuid, title, type, series_name, episode_number, season_number,
                   description, content_url, poster_url, runtime, genre_id, rating_id,
                   created_at, updated_at
            FROM content 
            WHERE series_name = 'Longstreet' AND title != 'Longstreet'
            ORDER BY episode_number, title
        """)
        episodes = cur.fetchall()
        
        print(f"📺 Episodes in Content Table ({len(episodes)} found):")
        for ep in episodes:
            print(f"\n   Episode {ep[5]}: {ep[2]} (ID: {ep[0]})")
            print(f"   UUID: {ep[1]}")
            print(f"   Type: {ep[3]}")
            print(f"   Series: {ep[4]}")
            print(f"   Season: {ep[6]}")
            print(f"   Description: {ep[7][:80]}..." if ep[7] else "No description")
            print(f"   Content URL: {ep[8] or 'None'}")
            print(f"   Poster URL: {ep[9] or 'None'}")
            print(f"   Runtime: {ep[10]} minutes")
            print(f"   Genre ID: {ep[11]}")
            print(f"   Rating ID: {ep[12]}")
            print(f"   Created: {ep[13]}")
            print(f"   Updated: {ep[14]}")
        
        print("\n" + "=" * 60)
        
        # Get episodes from episodes table
        cur.execute("""
            SELECT e.id, e.uuid, e.title, e.description, e.season_number, e.episode_number,
                   e.runtime, e.content_url, e.poster_url, e.air_date, e.series_id,
                   e.content_uuid, e.created_at, e.updated_at
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE c.title = 'Longstreet'
            ORDER BY e.episode_number, e.title
        """)
        episodes_table = cur.fetchall()
        
        print(f"📋 Episodes in Episodes Table ({len(episodes_table)} found):")
        for ep in episodes_table:
            print(f"\n   Episode {ep[5]}: {ep[2]} (ID: {ep[0]})")
            print(f"   UUID: {ep[1]}")
            print(f"   Description: {ep[3][:80]}..." if ep[3] else "No description")
            print(f"   Season: {ep[4]}")
            print(f"   Runtime: {ep[6]} minutes")
            print(f"   Content URL: {ep[7] or 'None'}")
            print(f"   Poster URL: {ep[8] or 'None'}")
            print(f"   Air Date: {ep[9] or 'None'}")
            print(f"   Series ID: {ep[10]}")
            print(f"   Content UUID: {ep[11]}")
            print(f"   Created: {ep[12]}")
            print(f"   Updated: {ep[13]}")
        
        print("\n" + "=" * 60)
        
        # Get genre and rating information
        cur.execute("""
            SELECT DISTINCT g.name as genre_name, r.code as rating_code
            FROM content c
            LEFT JOIN genres g ON c.genre_id = g.id
            LEFT JOIN ratings r ON c.rating_id = r.id
            WHERE c.series_name = 'Longstreet'
        """)
        metadata = cur.fetchall()
        
        print("🏷️  Genre and Rating Information:")
        for genre, rating in metadata:
            print(f"   Genre: {genre or 'None'}, Rating: {rating or 'None'}")
        
        print("\n" + "=" * 60)
        
        # Summary
        print("📊 Summary:")
        print(f"   Main Series: {'✅' if series else '❌'}")
        print(f"   Content Table Episodes: {len(episodes)}")
        print(f"   Episodes Table Entries: {len(episodes_table)}")
        print(f"   Episodes with Content URLs: {sum(1 for ep in episodes if ep[8])}")
        print(f"   Episodes with Poster URLs: {sum(1 for ep in episodes if ep[9])}")
        
        # Check for missing content URLs
        missing_content = [ep for ep in episodes if not ep[8]]
        if missing_content:
            print(f"\n⚠️  Episodes missing content URLs ({len(missing_content)}):")
            for ep in missing_content:
                print(f"   - {ep[2]} (Episode {ep[5]})")
        
        # Check for missing poster URLs
        missing_posters = [ep for ep in episodes if not ep[9]]
        if missing_posters:
            print(f"\n⚠️  Episodes missing poster URLs ({len(missing_posters)}):")
            for ep in missing_posters:
                print(f"   - {ep[2]} (Episode {ep[5]})")
        
        print("\n✅ Verification complete!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    verify_longstreet_status() 