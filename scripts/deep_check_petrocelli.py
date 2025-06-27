#!/usr/bin/env python3
"""
Script to deeply examine Petrocelli episodes database structure and find actual video filenames.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def deep_check_petrocelli():
    """Deep check of Petrocelli episodes database structure."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Deep checking Petrocelli episodes database structure...")
        print("=" * 70)
        
        # First, let's see the table structure
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'episodes'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("📋 Episodes table structure:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        print("\n" + "=" * 70)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        # Get ALL episodes with ALL fields
        cur.execute("""
            SELECT *
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        
        if not episodes:
            print("❌ No episodes found")
            return
        
        print(f"\n📺 Found {len(episodes)} episodes")
        print("=" * 70)
        
        # Show first few episodes with all their data
        for i, ep in enumerate(episodes[:5]):  # Show first 5 episodes
            print(f"\n🎬 Episode {ep['episode_number']}: {ep['title']}")
            print(f"  ID: {ep['id']}")
            print(f"  UUID: {ep['uuid']}")
            print(f"  Content URL: {ep['content_url']}")
            print(f"  Poster URL: {ep['poster_url']}")
            print(f"  Description: {ep['description'][:100]}...")
            print(f"  Season: {ep['season_number']}")
            print(f"  Runtime: {ep['runtime']}")
            print(f"  Air Date: {ep['air_date']}")
            print(f"  Created: {ep['created_at']}")
            print(f"  Updated: {ep['updated_at']}")
            print(f"  Content UUID: {ep['content_uuid']}")
            
            # Check if there are any other fields that might contain filenames
            for key, value in ep.items():
                if key not in ['id', 'uuid', 'title', 'description', 'season_number', 'episode_number', 
                              'runtime', 'content_url', 'poster_url', 'air_date', 'series_id', 
                              'created_at', 'updated_at', 'content_uuid']:
                    print(f"  {key}: {value}")
        
        # Let's also check if there are any other tables that might contain episode data
        print("\n" + "=" * 70)
        print("🔍 Checking for other tables that might contain episode data...")
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%episode%' OR table_name LIKE '%petrocelli%'
        """)
        
        related_tables = cur.fetchall()
        for table in related_tables:
            print(f"  Found table: {table['table_name']}")
            
            # Check if this table has Petrocelli data
            try:
                cur.execute(f"SELECT COUNT(*) as count FROM {table['table_name']}")
                count = cur.fetchone()
                print(f"    Records: {count['count']}")
                
                # If it has data, let's see the structure
                if count['count'] > 0:
                    cur.execute(f"SELECT * FROM {table['table_name']} LIMIT 1")
                    sample = cur.fetchone()
                    if sample:
                        print(f"    Sample fields: {list(sample.keys())}")
            except Exception as e:
                print(f"    Error checking table: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    deep_check_petrocelli() 