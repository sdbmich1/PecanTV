#!/usr/bin/env python3
"""
Fix final categorization issues:
- Move Mecklenburg from content table to Count of Monte Cristo episodes
- Move Please Leave the Wreck from Longstreet to Man with a Camera episodes
"""

import psycopg2
from datetime import datetime, timezone
import uuid

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_final_categorization():
    """Fix final categorization issues"""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔧 Fixing Final Categorization Issues")
        print("=" * 45)
        
        # 1. Get series IDs
        print("\n1. 🔍 Getting series IDs...")
        
        series_mapping = {
            'CMC': 'The Count of Monte Cristo',
            'MwC': 'Man with a Camera'
        }
        
        series_ids = {}
        for prefix, series_name in series_mapping.items():
            cur.execute("SELECT id, uuid FROM content WHERE title = %s AND type = 'SERIES'", (series_name,))
            series_record = cur.fetchone()
            if series_record:
                series_ids[prefix] = {'id': series_record[0], 'uuid': series_record[1]}
                print(f"   ✅ {series_name} (ID: {series_record[0]})")
            else:
                print(f"   ❌ {series_name} not found!")
        
        # 2. Move Mecklenburg from content table to CMC episodes
        print("\n2. 📦 Moving Mecklenburg to Count of Monte Cristo episodes...")
        
        # Get Mecklenburg from content table
        cur.execute("""
            SELECT id, title, content_url, poster_url, description, runtime, 
                   genre_id, rating_id, release_date, created_at, updated_at, uuid
            FROM content 
            WHERE title = 'Mecklenburg' AND type = 'SERIES'
        """)
        
        mecklenburg_data = cur.fetchone()
        if mecklenburg_data:
            content_id, title, content_url, poster_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at, content_uuid = mecklenburg_data
            
            # Get next episode number for CMC
            cmc_series_id = series_ids['CMC']['id']
            cur.execute("SELECT MAX(episode_number) FROM episodes WHERE series_id = %s AND season_number = 1", (cmc_series_id,))
            max_episode = cur.fetchone()[0] or 0
            next_episode = max_episode + 1
            
            # Generate new episode UUID
            episode_uuid = str(uuid.uuid4())
            
            # Insert into episodes table
            cur.execute("""
                INSERT INTO episodes (
                    uuid, title, description, season_number, episode_number, 
                    runtime, content_url, poster_url, series_id, content_uuid,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                episode_uuid, title, description, 1, next_episode,
                runtime, content_url, poster_url, cmc_series_id, content_uuid,
                created_at, updated_at
            ))
            
            # Delete from content table
            cur.execute("DELETE FROM content WHERE id = %s", (content_id,))
            
            print(f"   ✅ Moved 'Mecklenburg' to Count of Monte Cristo (episode {next_episode})")
        else:
            print("   ⚠️  Mecklenburg not found in content table")
        
        # 3. Move Please Leave the Wreck from Longstreet to Man with a Camera
        print("\n3. 🔄 Moving Please Leave the Wreck to Man with a Camera...")
        
        # Get the episode from Longstreet
        cur.execute("""
            SELECT id, title, description, runtime, content_url, poster_url, 
                   created_at, updated_at, uuid, content_uuid
            FROM episodes 
            WHERE title = 'Please Leave the Wreck for Others to Enjoy' AND series_id = 49
        """)
        
        please_leave_data = cur.fetchone()
        if please_leave_data:
            episode_id, title, description, runtime, content_url, poster_url, created_at, updated_at, episode_uuid, content_uuid = please_leave_data
            
            # Get next episode number for Man with a Camera
            mwc_series_id = series_ids['MwC']['id']
            cur.execute("SELECT MAX(episode_number) FROM episodes WHERE series_id = %s AND season_number = 1", (mwc_series_id,))
            max_episode = cur.fetchone()[0] or 0
            next_episode = max_episode + 1
            
            # Generate new UUIDs to avoid constraint violations
            new_episode_uuid = str(uuid.uuid4())
            new_content_uuid = str(uuid.uuid4())
            
            # Insert into episodes table with new series_id and new UUIDs
            cur.execute("""
                INSERT INTO episodes (
                    uuid, title, description, season_number, episode_number, 
                    runtime, content_url, poster_url, series_id, content_uuid,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                new_episode_uuid, title, description, 1, next_episode,
                runtime, content_url, poster_url, mwc_series_id, new_content_uuid,
                created_at, updated_at
            ))
            
            # Delete the old episode from Longstreet
            cur.execute("DELETE FROM episodes WHERE id = %s", (episode_id,))
            
            print(f"   ✅ Moved 'Please Leave the Wreck for Others to Enjoy' to Man with a Camera (episode {next_episode})")
        else:
            print("   ⚠️  Please Leave the Wreck not found in Longstreet episodes")
        
        # 4. Commit all changes
        conn.commit()
        
        print(f"\n✅ Successfully fixed final categorization!")
        
        # 5. Verify the fix
        print("\n4. 🔍 Verifying the fix...")
        
        # Check Mecklenburg
        cur.execute("SELECT title, episode_number, series_id FROM episodes WHERE title = 'Mecklenburg'")
        mecklenburg_result = cur.fetchone()
        if mecklenburg_result:
            title, episode_num, series_id = mecklenburg_result
            series_name = "Count of Monte Cristo" if series_id == cmc_series_id else "Unknown"
            print(f"   ✅ Mecklenburg: {title} (E{episode_num}, series: {series_name})")
        else:
            print("   ❌ Mecklenburg not found in episodes table")
        
        # Check Please Leave the Wreck
        cur.execute("SELECT title, episode_number, series_id FROM episodes WHERE title = 'Please Leave the Wreck for Others to Enjoy'")
        please_leave_result = cur.fetchone()
        if please_leave_result:
            title, episode_num, series_id = please_leave_result
            series_name = "Man with a Camera" if series_id == mwc_series_id else "Unknown"
            print(f"   ✅ Please Leave the Wreck: {title} (E{episode_num}, series: {series_name})")
        else:
            print("   ❌ Please Leave the Wreck not found in episodes table")
        
        # Check content table for remaining issues
        cur.execute("SELECT title, type FROM content WHERE title IN ('Mecklenburg', 'Please Leave the Wreck for Others to Enjoy')")
        remaining_issues = cur.fetchall()
        if remaining_issues:
            print("   ⚠️  Remaining issues found:")
            for title, content_type in remaining_issues:
                print(f"      - {title} (type: {content_type})")
        else:
            print("   ✅ No remaining categorization issues found!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_final_categorization() 