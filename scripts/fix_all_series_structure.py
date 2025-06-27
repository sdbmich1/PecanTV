#!/usr/bin/env python3
"""
Script to fix all series structure by removing duplicate episode records from content table
when they already exist in the episodes table.
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

def fix_all_series_structure():
    """Fix all series structure by removing duplicate episode records."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing All Series Structure")
        print("=" * 50)
        
        # Get all unique series from episodes table (join with content to get series names)
        cur.execute("""
            SELECT DISTINCT c.title as series_name, c.id as series_id
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE c.type = 'SERIES'
            ORDER BY c.title
        """)
        series_list = [(row[0], row[1]) for row in cur.fetchall()]
        
        print(f"📺 Found {len(series_list)} series with episodes:")
        for series_name, series_id in series_list:
            print(f"  - {series_name} (ID: {series_id})")
        
        if not series_list:
            print("❌ No series found in episodes table")
            return
        
        # For each series, remove duplicate episode records from content table
        total_removed = 0
        
        for series_name, series_id in series_list:
            print(f"\n🎬 Processing series: {series_name}")
            
            # Get all episode titles for this series from episodes table
            cur.execute("""
                SELECT title FROM episodes 
                WHERE series_id = %s
            """, (series_id,))
            episode_titles = [row[0] for row in cur.fetchall()]
            
            print(f"  📺 Found {len(episode_titles)} episodes in episodes table")
            
            # Remove any content records with these episode titles (except the main series)
            for episode_title in episode_titles:
                cur.execute("""
                    DELETE FROM content 
                    WHERE title = %s AND title != %s
                """, (episode_title, series_name))
                
                if cur.rowcount > 0:
                    print(f"    🗑️  Removed duplicate content record: {episode_title}")
                    total_removed += cur.rowcount
        
        # Commit changes
        conn.commit()
        
        print(f"\n📊 Summary:")
        print("-" * 40)
        print(f"Series processed: {len(series_list)}")
        print(f"Total duplicate records removed: {total_removed}")
        print("\n✅ All series structure cleanup complete!")
        
        # Show final state
        print(f"\n📋 Final state check:")
        print("-" * 40)
        
        for series_name, series_id in series_list:
            # Count episodes in episodes table
            cur.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (series_id,))
            episodes_count = cur.fetchone()[0]
            
            # Count content records for this series (excluding main series)
            cur.execute("""
                SELECT COUNT(*) FROM content 
                WHERE series_name = %s AND title != %s
            """, (series_name, series_name))
            content_count = cur.fetchone()[0]
            
            print(f"  {series_name}:")
            print(f"    Episodes table: {episodes_count} records")
            print(f"    Content table: {content_count} records")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_all_series_structure() 