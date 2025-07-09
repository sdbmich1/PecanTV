#!/usr/bin/env python3
"""
Fix all episode issues: misplaced episodes, incorrect titles, missing episodes
"""

import psycopg2
import uuid
from datetime import datetime, timezone

DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_all_episode_issues():
    print("🔧 Fixing all episode issues...")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 1. Fix misplaced Mike Hammer episode in Longstreet
        print("\n1. Fixing misplaced Mike Hammer episode in Longstreet...")
        cur.execute("""
            SELECT id, title FROM episodes 
            WHERE series_id = 49 AND title = 'For Sale: Death Bed-Used'
        """)
        misplaced_episode = cur.fetchone()
        
        if misplaced_episode:
            episode_id, title = misplaced_episode
            print(f"  Found misplaced episode: {title}")
            
            # Check if it already exists in Mike Hammer
            cur.execute("""
                SELECT id FROM episodes 
                WHERE series_id = 45 AND title = 'For Sale: Death Bed-Used'
            """)
            existing = cur.fetchone()
            
            if existing:
                print("  Episode already exists in Mike Hammer, deleting from Longstreet")
                cur.execute("DELETE FROM episodes WHERE id = %s", (episode_id,))
            else:
                # Check if Mike Hammer episode 2 already exists
                cur.execute("""
                    SELECT id FROM episodes 
                    WHERE series_id = 45 AND episode_number = 2
                """)
                mh_ep2 = cur.fetchone()
                
                if mh_ep2:
                    print("  Mike Hammer episode 2 exists, deleting misplaced episode from Longstreet")
                    cur.execute("DELETE FROM episodes WHERE id = %s", (episode_id,))
                else:
                    print("  Moving episode to Mike Hammer as episode 2")
                    cur.execute("""
                        UPDATE episodes 
                        SET series_id = 45, episode_number = 2, updated_at = %s
                        WHERE id = %s
                    """, (datetime.now(timezone.utc), episode_id))
        
        # 2. Fix Mike Hammer episode titles
        print("\n2. Fixing Mike Hammer episode titles...")
        mike_hammer_episodes = [
            (1, "Music To Die By"),
            (2, "For Sale: Death Bed-Used"),
            (3, "Shots in the Dark"),
            (4, "The Girl in the Red Bikini")
        ]
        
        for episode_num, correct_title in mike_hammer_episodes:
            cur.execute("""
                UPDATE episodes 
                SET title = %s, updated_at = %s
                WHERE series_id = 45 AND episode_number = %s
            """, (correct_title, datetime.now(timezone.utc), episode_num))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated S1E{episode_num}: {correct_title}")
        
        # 3. Check Ghost Squad episodes
        print("\n3. Checking Ghost Squad episodes...")
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = 72")
        ghost_squad_count = cur.fetchone()[0]
        print(f"  Ghost Squad episodes: {ghost_squad_count}")
        
        if ghost_squad_count == 0:
            print("  ⚠️  No Ghost Squad episodes found!")
            print("  Need to restore Ghost Squad episodes")
        
        # 4. Verify Longstreet episodes
        print("\n4. Verifying Longstreet episodes...")
        cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = 49")
        longstreet_count = cur.fetchone()[0]
        print(f"  Longstreet episodes: {longstreet_count}")
        
        # Check if Longstreet episode 1 is correct
        cur.execute("""
            SELECT title FROM episodes 
            WHERE series_id = 49 AND episode_number = 1
        """)
        episode1 = cur.fetchone()
        if episode1:
            print(f"  Longstreet S1E1: {episode1[0]}")
            if "Death Bed" in episode1[0]:
                print("  ⚠️  Longstreet still has misplaced episode!")
        
        conn.commit()
        
        # Final verification
        print("\n5. Final verification...")
        series_checks = [
            (45, "Mike Hammer"),
            (49, "Longstreet"),
            (68, "Dragnet"),
            (72, "Ghost Squad")
        ]
        
        for series_id, series_name in series_checks:
            cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
            count = cur.fetchone()[0]
            print(f"  {series_name}: {count} episodes")
        
        conn.close()
        print("\n✅ All episode issues fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_all_episode_issues() 