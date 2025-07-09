#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def fix_longstreet_episodes():
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Get Longstreet series ID
        cursor.execute("SELECT id FROM content WHERE title ILIKE %s AND type = %s", ('%longstreet%', 'SERIES'))
        series_id = cursor.fetchone()[0]
        
        print(f"Found Longstreet series ID: {series_id}")
        
        # First, update all episode runtimes to 60 minutes
        cursor.execute("""
            UPDATE episodes 
            SET runtime = 60
            WHERE series_id = %s
        """, (series_id,))
        
        print("Updated all episode runtimes to 60 minutes")
        
        # Get the "Beginnings" episode (currently episode 22)
        cursor.execute("""
            SELECT id FROM episodes 
            WHERE series_id = %s AND title = 'Beginnings'
        """, (series_id,))
        
        beginnings_episode_id = cursor.fetchone()[0]
        
        # Set "Beginnings" to episode 0
        cursor.execute("""
            UPDATE episodes 
            SET episode_number = 0
            WHERE id = %s
        """, (beginnings_episode_id,))
        print("Set 'Beginnings' to episode 0")
        
        # Shift all other episodes up by 1, in descending order
        cursor.execute("""
            SELECT id, episode_number FROM episodes 
            WHERE series_id = %s AND id != %s
            ORDER BY episode_number DESC
        """, (series_id, beginnings_episode_id))
        episodes = cursor.fetchall()
        for ep_id, ep_num in episodes:
            cursor.execute("UPDATE episodes SET episode_number = %s WHERE id = %s", (ep_num + 1, ep_id))
        print("Shifted all other episodes up by 1 in descending order")
        
        # Set "Beginnings" to episode 1
        cursor.execute("""
            UPDATE episodes 
            SET episode_number = 1
            WHERE id = %s
        """, (beginnings_episode_id,))
        print("Set 'Beginnings' to episode 1")
        
        conn.commit()
        print("Successfully updated Longstreet episodes")
        
        # Verify the changes
        cursor.execute("""
            SELECT episode_number, title, runtime
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cursor.fetchall()
        print(f"\nVerification - Found {len(episodes)} episodes:")
        for ep in episodes:
            print(f"Episode {ep[0]}: {ep[1]} - Runtime: {ep[2]} min")
        
    except Exception as e:
        print(f"Error updating episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Fixing Longstreet episode runtimes and reordering...")
    fix_longstreet_episodes() 