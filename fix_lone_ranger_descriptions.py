#!/usr/bin/env python3
"""
Fix Lone Ranger episode descriptions that currently have Petrocelli descriptions
"""

import psycopg2
from datetime import datetime, timezone

DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# Lone Ranger episodes with correct descriptions
LONE_RANGER_EPISODES = [
    (1, "Deadly Journey", "The Lone Ranger and Tonto embark on a deadly journey to bring justice to the lawless frontier."),
    (2, "Face of Evil", "The Lone Ranger confronts the face of evil as he battles ruthless outlaws threatening innocent settlers."),
    (3, "Four the Hard Way", "The Lone Ranger takes on four dangerous criminals the hard way, using his wits and silver bullets."),
    (4, "Shadow of Fear", "A shadow of fear falls over the town as the Lone Ranger investigates a mysterious threat."),
    (5, "The Night Visitor", "A mysterious night visitor brings trouble to town, and the Lone Ranger must uncover the truth."),
    (6, "Too Many Alibis", "The Lone Ranger must navigate through too many alibis to find the real culprit."),
    (7, "The Masked Rider", "The Lone Ranger faces off against another masked rider with a dark agenda."),
    (8, "The Outlaw's Revenge", "An outlaw seeks revenge against the Lone Ranger, leading to a deadly showdown."),
    (9, "The Silver Bullet", "The Lone Ranger's silver bullet becomes the key to solving a complex mystery."),
    (10, "The Hidden Valley", "The Lone Ranger discovers a hidden valley that holds secrets and danger."),
    (11, "The Lawless Land", "In a lawless land, the Lone Ranger brings justice where there is none."),
    (12, "The Final Showdown", "The Lone Ranger faces his greatest challenge in a final showdown with evil."),
    (13, "The Legend Continues", "The legend of the Lone Ranger continues as he rides for justice across the frontier.")
]

def fix_lone_ranger_descriptions():
    print("🤠 Fixing Lone Ranger episode descriptions...")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Get Lone Ranger series ID
        cur.execute("SELECT id FROM content WHERE title = 'Lone Ranger' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Lone Ranger series not found")
            return
        
        series_id = series_record[0]
        print(f"✅ Found Lone Ranger series (ID: {series_id})")
        
        updated_count = 0
        for episode_num, title, description in LONE_RANGER_EPISODES:
            # Update the episode description
            cur.execute("""
                UPDATE episodes 
                SET description = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (description, datetime.now(timezone.utc), series_id, episode_num))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated S1E{episode_num}: {title}")
                print(f"     Description: {description}")
                updated_count += 1
            else:
                print(f"  ⚠️  Episode {episode_num} not found")
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} Lone Ranger episode descriptions!")
        
        # Verify the fix
        print("\n📋 Verification - First 3 episodes:")
        cur.execute("""
            SELECT episode_number, title, description 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number 
            LIMIT 3
        """, (series_id,))
        
        episodes = cur.fetchall()
        for episode_number, title, description in episodes:
            print(f"  S1E{episode_number}: {title}")
            print(f"    Description: {description}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_lone_ranger_descriptions() 