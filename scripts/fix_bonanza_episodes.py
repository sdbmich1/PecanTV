#!/usr/bin/env python3
"""
Script to fix Bonanza episodes by removing duplicates and fixing episode numbering.
"""

import psycopg2
import uuid
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

def fix_bonanza_episodes():
    """Fix Bonanza episodes by removing duplicates and fixing episode numbering."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing Bonanza Episodes")
        print("=" * 40)
        
        # Get Bonanza series ID
        cur.execute('SELECT id FROM content WHERE type = %s AND title = %s', ('SERIES', 'Bonanza'))
        series_id = cur.fetchone()[0]
        print(f"✅ Found Bonanza series (ID: {series_id})")
        
        # Get all current Bonanza episodes
        cur.execute('''
            SELECT id, title, season_number, episode_number
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY season_number, episode_number, title
        ''', (series_id,))
        
        episodes = cur.fetchall()
        print(f"📋 Current episodes: {len(episodes)}")
        
        # Group by title to find duplicates
        title_groups = {}
        for ep in episodes:
            title = ep[1]
            if title in title_groups:
                title_groups[title].append(ep)
            else:
                title_groups[title] = [ep]
        
        # Find unique episodes (keep one per title)
        unique_episodes = []
        duplicates_to_remove = []
        
        for title, eps in title_groups.items():
            if len(eps) > 1:
                # Keep the first one, mark others for deletion
                unique_episodes.append(eps[0])
                duplicates_to_remove.extend(eps[1:])
                print(f"  ⚠️  Found {len(eps)} duplicates for '{title}' - keeping first, removing {len(eps)-1}")
            else:
                unique_episodes.append(eps[0])
        
        print(f"📊 Analysis:")
        print(f"  • Unique episodes: {len(unique_episodes)}")
        print(f"  • Duplicates to remove: {len(duplicates_to_remove)}")
        
        # Remove duplicates
        if duplicates_to_remove:
            duplicate_ids = [ep[0] for ep in duplicates_to_remove]
            cur.execute('DELETE FROM episodes WHERE id = ANY(%s)', (duplicate_ids,))
            print(f"  ✅ Removed {len(duplicates_to_remove)} duplicate episodes")
        
        # Sort unique episodes by current episode number
        unique_episodes.sort(key=lambda x: x[3])  # Sort by episode_number
        
        # Fix episode numbering to be sequential
        print(f"\n🔢 Fixing Episode Numbers:")
        for i, episode in enumerate(unique_episodes, 1):
            old_episode_num = episode[3]
            new_episode_num = i
            
            if old_episode_num != new_episode_num:
                print(f"  • '{episode[1]}': S1E{old_episode_num} → S1E{new_episode_num}")
                cur.execute('''
                    UPDATE episodes 
                    SET episode_number = %s, updated_at = %s
                    WHERE id = %s
                ''', (new_episode_num, datetime.now(timezone.utc), episode[0]))
            else:
                print(f"  • '{episode[1]}': S1E{old_episode_num} (no change)")
        
        conn.commit()
        
        # Verify final result
        cur.execute('''
            SELECT title, season_number, episode_number
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY season_number, episode_number
        ''', (series_id,))
        
        final_episodes = cur.fetchall()
        print(f"\n✅ Final Result:")
        print(f"  • Total episodes: {len(final_episodes)}")
        print(f"  • Episode range: S1E1 - S1E{len(final_episodes)}")
        
        print(f"\n📺 Final Episode List:")
        for ep in final_episodes:
            print(f"  • S{ep[1]}E{ep[2]}: {ep[0]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_bonanza_episodes() 