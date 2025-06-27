#!/usr/bin/env python3
"""
Script to check all existing Petrocelli data in episodes and content tables.
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

def check_existing_petrocelli_data():
    """Check all existing Petrocelli data in episodes and content tables."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Checking all existing Petrocelli data in database...")
        print("=" * 70)
        
        # Check episodes table
        print("\n📺 EPISODES TABLE:")
        print("-" * 40)
        
        cur.execute("""
            SELECT id, episode_number, title, content_url, description
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES')
            ORDER BY episode_number
        """)
        
        episodes = cur.fetchall()
        
        for ep in episodes:
            filename = ep['content_url'].split('/')[-1] if ep['content_url'] else 'No URL'
            print(f"Episode {ep['episode_number']}: {ep['title']}")
            print(f"  Content URL: {ep['content_url']}")
            print(f"  Filename: {filename}")
            print()
        
        # Check content table for all Petrocelli entries
        print("\n🎬 CONTENT TABLE:")
        print("-" * 40)
        
        cur.execute("""
            SELECT id, title, type, content_url, poster_url, description, series_name
            FROM content 
            WHERE (title ILIKE '%petrocelli%' OR series_name ILIKE '%petrocelli%')
            ORDER BY title
        """)
        
        content_entries = cur.fetchall()
        
        for entry in content_entries:
            filename = entry['content_url'].split('/')[-1] if entry['content_url'] else 'No URL'
            print(f"{entry['title']} (Type: {entry['type']})")
            print(f"  Content URL: {entry['content_url']}")
            print(f"  Filename: {filename}")
            print(f"  Series Name: {entry['series_name']}")
            print()
        
        # Check if there are any other tables with Petrocelli data
        print("\n🔍 OTHER TABLES WITH PETROCELLI DATA:")
        print("-" * 40)
        
        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        
        for table in tables:
            table_name = table['table_name']
            
            # Check if this table has Petrocelli data
            try:
                cur.execute(f"""
                    SELECT COUNT(*) as count 
                    FROM {table_name} 
                    WHERE title ILIKE '%petrocelli%' OR series_name ILIKE '%petrocelli%'
                """)
                result = cur.fetchone()
                if result['count'] > 0:
                    print(f"  Found {result['count']} Petrocelli records in {table_name}")
                    
                    # Show sample data
                    cur.execute(f"""
                        SELECT * 
                        FROM {table_name} 
                        WHERE title ILIKE '%petrocelli%' OR series_name ILIKE '%petrocelli%'
                        LIMIT 3
                    """)
                    samples = cur.fetchall()
                    for sample in samples:
                        print(f"    Sample: {dict(sample)}")
            except Exception as e:
                # Skip if table doesn't have title or series_name columns
                pass
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_existing_petrocelli_data() 