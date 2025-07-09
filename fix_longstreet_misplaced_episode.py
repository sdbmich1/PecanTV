#!/usr/bin/env python3
"""
Fix misplaced Mike Hammer episode in Longstreet series
"""

import psycopg2
from datetime import datetime, timezone

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def fix_misplaced_episode():
    print("🔧 Fixing misplaced Mike Hammer episode in Longstreet...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Find the misplaced episode
        cur.execute("""
            SELECT id, title, content_url FROM episodes 
            WHERE series_id = 49 AND title = 'For Sale: Death Bed-Used'
        """)
        episode = cur.fetchone()
        
        if not episode:
            print("❌ Misplaced episode not found")
            return
        
        episode_id, title, content_url = episode
        print(f"📺 Found misplaced episode: {title}")
        print(f"   Content URL: {content_url}")
        
        # Check if this episode already exists in Mike Hammer
        cur.execute("""
            SELECT id FROM episodes 
            WHERE series_id = 45 AND title = 'For Sale: Death Bed-Used'
        """)
        existing = cur.fetchone()
        
        if existing:
            print("⚠️  Episode already exists in Mike Hammer, deleting from Longstreet")
            # Delete from Longstreet
            cur.execute("DELETE FROM episodes WHERE id = %s", (episode_id,))
            print(f"  ✅ Deleted episode {episode_id} from Longstreet")
        else:
            print("🔄 Moving episode to Mike Hammer series")
            # Update the episode to belong to Mike Hammer
            cur.execute("""
                UPDATE episodes 
                SET series_id = 45, updated_at = %s
                WHERE id = %s
            """, (datetime.now(timezone.utc), episode_id))
            print(f"  ✅ Moved episode {episode_id} to Mike Hammer (series_id = 45)")
        
        conn.commit()
        
        # Verify the fix
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = 49")
        longstreet_count = cur.fetchone()[0]
        print(f"📊 Longstreet episodes after fix: {longstreet_count}")
        
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = 45")
        mike_hammer_count = cur.fetchone()[0]
        print(f"📊 Mike Hammer episodes after fix: {mike_hammer_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_misplaced_episode() 