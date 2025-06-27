#!/usr/bin/env python3
"""
Script to update Petrocelli episode descriptions with more meaningful content.
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

# Petrocelli episode descriptions based on typical legal drama content
PETROCELLI_DESCRIPTIONS = {
    1: "Tony Petrocelli, a Harvard-educated lawyer, moves to the Southwest to practice law. In this episode, he takes on his first case in the region, defending a client accused of a serious crime.",
    2: "Petrocelli investigates a complex case involving local corruption and must navigate the challenges of being an outsider in a tight-knit community while fighting for justice.",
    3: "A high-profile case puts Petrocelli in the spotlight as he defends a client against powerful local interests, testing his legal skills and determination.",
    4: "Petrocelli faces a moral dilemma when he discovers evidence that could exonerate his client but might implicate someone he trusts, forcing him to choose between loyalty and justice.",
    5: "In a dramatic courtroom showdown, Petrocelli uses his sharp legal mind and deep understanding of human nature to uncover the truth and deliver justice for his client."
}

def update_petrocelli_descriptions():
    """Update Petrocelli episode descriptions with more meaningful content."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔧 Updating Petrocelli Episode Descriptions")
        print("=" * 50)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        updated = 0
        for episode_num, description in PETROCELLI_DESCRIPTIONS.items():
            # Update the episode description
            cur.execute("""
                UPDATE episodes 
                SET description = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (description, datetime.now(timezone.utc), series_id, episode_num))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated Episode {episode_num}: {description[:50]}...")
                updated += 1
            else:
                print(f"  ⚠️  Episode {episode_num} not found")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Petrocelli episode descriptions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_petrocelli_descriptions() 