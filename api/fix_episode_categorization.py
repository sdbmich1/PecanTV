#!/usr/bin/env python3
"""
Fix episode categorization by moving episodes from content table to episodes table
"""

import os
import uuid
from sqlalchemy import create_engine, text
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def main():
    print("🔧 Fixing episode categorization...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Define episode mappings
        episode_mappings = [
            {
                'content_id': 556,
                'title': "Wednesday's Child",
                'content_url': "https://storage.googleapis.com/pecantv_features/Longstreet-Wednesdays-Child_2p-1080-withCredits.mp4",
                'series_id': 49,  # Longstreet
                'episode_number': None  # Will be determined
            },
            {
                'content_id': 562,
                'title': "Let the Memories Be Happy Ones",
                'content_url': "https://storage.googleapis.com/pecantv_features/Longstreet-Let-the-Memories-Be-Happy-Ones_2p-1080-withCredits.mp4",
                'series_id': 49,  # Longstreet
                'episode_number': None  # Will be determined
            },
            {
                'content_id': 600,
                'title': "Return to the Chateau d'if",
                'content_url': "https://storage.googleapis.com/pecantv_features/CMC30-return-to-the-chateau-d'if_2p-1080-wCredits.mp4",
                'series_id': 72,  # Count of Monte Cristo
                'episode_number': None  # Will be determined
            },
            {
                'content_id': 584,
                'title': "Mecklenburg",
                'content_url': "https://storage.googleapis.com/pecantv_features/CMC14-mecklenburg_2p-1080-wCredits.mp4",
                'series_id': 72,  # Count of Monte Cristo
                'episode_number': None  # Will be determined
            }
        ]
        
        # Process each episode
        for episode in episode_mappings:
            print(f"\n📺 Processing: {episode['title']}")
            
            # Get episode data from content table
            result = conn.execute(text("""
                SELECT id, title, content_url, poster_url, description, runtime, release_date, 
                       genre_id, rating_id, created_at, updated_at, uuid
                FROM content 
                WHERE id = :content_id
            """), {'content_id': episode['content_id']})
            
            content_row = result.fetchone()
            if not content_row:
                print(f"❌ Content with ID {episode['content_id']} not found")
                continue
            content_uuid = content_row[11]
            
            # Determine episode number based on URL pattern
            if episode['series_id'] == 49:  # Longstreet
                # Extract episode number from URL if possible
                if 'Longstreet-' in content_row[2]:
                    # Try to find episode number in existing episodes
                    result = conn.execute(text("""
                        SELECT MAX(episode_number) FROM episodes WHERE series_id = 49
                    """))
                    max_ep = result.fetchone()[0]
                    episode['episode_number'] = (max_ep or 0) + 1
                else:
                    episode['episode_number'] = 1
            elif episode['series_id'] == 72:  # Count of Monte Cristo
                # Extract episode number from URL (CMC14, CMC30, etc.)
                if 'CMC' in content_row[2]:
                    import re
                    match = re.search(r'CMC(\d+)', content_row[2])
                    if match:
                        episode['episode_number'] = int(match.group(1))
                    else:
                        # Fallback: get next episode number
                        result = conn.execute(text("""
                            SELECT MAX(episode_number) FROM episodes WHERE series_id = 72
                        """))
                        max_ep = result.fetchone()[0]
                        episode['episode_number'] = (max_ep or 0) + 1
                else:
                    episode['episode_number'] = 1
            
            print(f"   📝 Series ID: {episode['series_id']}, Episode: {episode['episode_number']}")
            
            # Generate new UUID for episodes table
            episode_uuid = str(uuid.uuid4())
            
            # Insert into episodes table
            try:
                conn.execute(text("""
                    INSERT INTO episodes (
                        series_id, season_number, title, episode_number, content_url, poster_url, 
                        description, runtime, air_date, created_at, updated_at, uuid, content_uuid
                    ) VALUES (
                        :series_id, :season_number, :title, :episode_number, :content_url, :poster_url,
                        :description, :runtime, :air_date, :created_at, :updated_at, :uuid, :content_uuid
                    )
                """), {
                    'series_id': episode['series_id'],
                    'season_number': 1,
                    'title': content_row[1],
                    'episode_number': episode['episode_number'],
                    'content_url': content_row[2],
                    'poster_url': content_row[3],
                    'description': content_row[4],
                    'runtime': content_row[5],
                    'air_date': content_row[6],
                    'created_at': content_row[9] or datetime.utcnow(),
                    'updated_at': content_row[10] or datetime.utcnow(),
                    'uuid': episode_uuid,
                    'content_uuid': content_uuid
                })
                
                print(f"   ✅ Added to episodes table")
                
                # Delete from content table
                conn.execute(text("DELETE FROM content WHERE id = :id"), {'id': episode['content_id']})
                print(f"   🗑️  Removed from content table")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ All changes committed successfully!")
        
        # Verify the changes
        print(f"\n🔍 Verification:")
        for episode in episode_mappings:
            if episode['series_id'] == 49:
                series_name = "Longstreet"
            elif episode['series_id'] == 72:
                series_name = "Count of Monte Cristo"
            else:
                series_name = f"Series {episode['series_id']}"
            
            result = conn.execute(text("""
                SELECT COUNT(*) FROM episodes 
                WHERE series_id = :series_id AND title = :title
            """), {
                'series_id': episode['series_id'],
                'title': episode['title']
            })
            
            count = result.fetchone()[0]
            if count > 0:
                print(f"   ✅ {episode['title']} found in {series_name} episodes")
            else:
                print(f"   ❌ {episode['title']} NOT found in {series_name} episodes")

if __name__ == "__main__":
    main() 