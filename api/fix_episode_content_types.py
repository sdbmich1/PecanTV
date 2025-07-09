#!/usr/bin/env python3
"""
Fix episode content types by moving episodes to the episodes table
and cleaning up the series_name field.
"""

import psycopg2
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

def fix_episode_content_types():
    """Move episode content to episodes table and clean up content table."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔧 Fixing Episode Content Types")
        print("=" * 50)
        
        # 1. Find all content with type = 'EPISODE'
        cur.execute("""
            SELECT id, uuid, title, description, content_url, poster_url, 
                   series_name, episode_number, season_number, genre_id, rating_id
            FROM content 
            WHERE type = 'EPISODE'
        """)
        
        episode_content = cur.fetchall()
        print(f"Found {len(episode_content)} episode records in content table")
        
        if not episode_content:
            print("✅ No episode content to fix")
            return
        
        # 2. Process each episode
        for record in episode_content:
            content_id, content_uuid, title, description, content_url, poster_url, \
            series_name, episode_number, season_number, genre_id, rating_id = record
            
            print(f"\n📺 Processing: {title}")
            print(f"   Series: {series_name}")
            print(f"   Episode: {episode_number}")
            
            # 3. Find the corresponding series
            if series_name:
                cur.execute("""
                    SELECT id, uuid FROM content 
                    WHERE type = 'SERIES' AND title = %s
                """, (series_name,))
                series_record = cur.fetchone()
                
                if series_record:
                    series_id, series_uuid = series_record
                    print(f"   ✅ Found series: {series_name} (ID: {series_id})")
                    
                    # 4. Check if episode already exists in episodes table
                    cur.execute("""
                        SELECT id FROM episodes 
                        WHERE series_id = %s AND episode_number = %s
                    """, (series_id, episode_number or 1))
                    
                    if not cur.fetchone():
                        # 5. Insert into episodes table
                        cur.execute("""
                            INSERT INTO episodes (
                                uuid, title, description, season_number, episode_number,
                                runtime, content_url, poster_url, air_date, series_id, 
                                content_uuid, created_at, updated_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """, (
                            str(content_uuid),
                            title,
                            description or f"Episode of {series_name}",
                            season_number or 1,
                            episode_number or 1,
                            60,  # Default runtime
                            content_url or '',
                            poster_url or '',
                            None,  # Air date
                            series_id,
                            str(series_uuid),
                            datetime.now(timezone.utc),
                            datetime.now(timezone.utc)
                        ))
                        
                        print(f"   ✅ Added to episodes table")
                        
                        # 6. Delete from content table
                        cur.execute("DELETE FROM content WHERE id = %s", (content_id,))
                        print(f"   ✅ Removed from content table")
                    else:
                        print(f"   ⚠️  Episode already exists in episodes table")
                        # Still delete from content table
                        cur.execute("DELETE FROM content WHERE id = %s", (content_id,))
                        print(f"   ✅ Removed from content table")
                else:
                    print(f"   ❌ Series not found: {series_name}")
                    # Convert to FILM since we can't find the series
                    cur.execute("""
                        UPDATE content 
                        SET type = 'FILM', series_name = NULL, episode_number = NULL, season_number = NULL
                        WHERE id = %s
                    """, (content_id,))
                    print(f"   ✅ Converted to FILM")
            else:
                print(f"   ❌ No series name found")
                # Convert to FILM
                cur.execute("""
                    UPDATE content 
                    SET type = 'FILM', series_name = NULL, episode_number = NULL, season_number = NULL
                    WHERE id = %s
                """, (content_id,))
                print(f"   ✅ Converted to FILM")
        
        # 7. Remove series_name field from content table (optional - can be done later)
        print(f"\n🧹 Cleaning up content table...")
        
        # Update SERIES type content to remove redundant series_name
        cur.execute("""
            UPDATE content 
            SET series_name = NULL 
            WHERE type = 'SERIES'
        """)
        print(f"   ✅ Removed series_name from SERIES records")
        
        # Update FILM type content to remove series_name
        cur.execute("""
            UPDATE content 
            SET series_name = NULL 
            WHERE type = 'FILM'
        """)
        print(f"   ✅ Removed series_name from FILM records")
        
        conn.commit()
        print(f"\n✅ Successfully fixed episode content types!")
        
        # 8. Verify the fix
        print(f"\n📊 Verification:")
        cur.execute("SELECT type, COUNT(*) FROM content GROUP BY type ORDER BY COUNT(*) DESC")
        type_counts = cur.fetchall()
        for content_type, count in type_counts:
            print(f"   {content_type}: {count}")
        
        cur.execute("SELECT COUNT(*) FROM episodes")
        episode_count = cur.fetchone()[0]
        print(f"   Episodes table: {episode_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_episode_content_types() 