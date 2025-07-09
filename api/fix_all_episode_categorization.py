#!/usr/bin/env python3
"""
Fix all episode categorization by moving episodes from content table to episodes table
"""

import os
import uuid
import re
from sqlalchemy import create_engine, text
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def get_series_id_from_url(content_url):
    """Determine series ID based on content URL pattern"""
    if 'Longstreet-' in content_url:
        return 49  # Longstreet
    elif 'CMC' in content_url:
        return 72  # Count of Monte Cristo
    elif 'GS-' in content_url:
        return 78  # Ghost Squad (assuming this is the correct ID)
    elif 'Bonanza-' in content_url:
        return 68  # Bonanza (assuming this is the correct ID)
    else:
        return None

def get_episode_number_from_url(content_url, series_id):
    """Extract episode number from URL"""
    if series_id == 49:  # Longstreet
        # For Longstreet, we'll assign sequential numbers
        return None  # Will be determined by max episode + 1
    elif series_id == 72:  # Count of Monte Cristo
        match = re.search(r'CMC(\d+)', content_url)
        if match:
            return int(match.group(1))
        return None
    elif series_id == 78:  # Ghost Squad
        # For GS, we'll assign sequential numbers
        return None
    elif series_id == 68:  # Bonanza
        # For Bonanza, we'll assign sequential numbers
        return None
    return None

def main():
    print("🔧 Fixing all episode categorization...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all episodes that need to be moved
        result = conn.execute(text("""
            SELECT id, title, content_url, poster_url, description, runtime, release_date, 
                   genre_id, rating_id, created_at, updated_at, uuid
            FROM content 
            WHERE content_url ILIKE '%Longstreet-%' 
               OR content_url ILIKE '%CMC%' 
               OR content_url ILIKE '%GS-%'
               OR content_url ILIKE '%Bonanza-%'
            ORDER BY title
        """))
        
        episodes_to_move = result.fetchall()
        print(f"Found {len(episodes_to_move)} episodes to move")
        
        # Track episode numbers for each series
        episode_counters = {
            49: 0,  # Longstreet
            72: 0,  # Count of Monte Cristo
            78: 0,  # Ghost Squad
            68: 0   # Bonanza
        }
        
        # Get current max episode numbers
        for series_id in episode_counters.keys():
            result = conn.execute(text("""
                SELECT MAX(episode_number) FROM episodes WHERE series_id = :series_id
            """), {'series_id': series_id})
            max_ep = result.fetchone()[0]
            episode_counters[series_id] = (max_ep or 0) + 1
        
        print(f"Current episode counters: {episode_counters}")
        
        # Process each episode
        for content_row in episodes_to_move:
            content_id, title, content_url, poster_url, description, runtime, release_date, genre_id, rating_id, created_at, updated_at, content_uuid = content_row
            
            print(f"\n📺 Processing: {title}")
            
            # Determine series ID
            series_id = get_series_id_from_url(content_url)
            if not series_id:
                print(f"   ❌ Could not determine series for: {title}")
                continue
            
            # Determine episode number
            episode_number = get_episode_number_from_url(content_url, series_id)
            if episode_number is None:
                episode_number = episode_counters[series_id]
                episode_counters[series_id] += 1
            
            print(f"   📝 Series ID: {series_id}, Episode: {episode_number}")
            
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
                    'series_id': series_id,
                    'season_number': 1,
                    'title': title,
                    'episode_number': episode_number,
                    'content_url': content_url,
                    'poster_url': poster_url,
                    'description': description,
                    'runtime': runtime,
                    'air_date': release_date,
                    'created_at': created_at or datetime.utcnow(),
                    'updated_at': updated_at or datetime.utcnow(),
                    'uuid': episode_uuid,
                    'content_uuid': content_uuid
                })
                
                print(f"   ✅ Added to episodes table")
                
                # Delete from content table
                conn.execute(text("DELETE FROM content WHERE id = :id"), {'id': content_id})
                print(f"   🗑️  Removed from content table")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ All changes committed successfully!")
        
        # Verify the changes
        print(f"\n🔍 Verification:")
        series_names = {49: "Longstreet", 72: "Count of Monte Cristo", 78: "Ghost Squad", 68: "Bonanza"}
        
        for series_id, series_name in series_names.items():
            result = conn.execute(text("""
                SELECT COUNT(*) FROM episodes WHERE series_id = :series_id
            """), {'series_id': series_id})
            
            count = result.fetchone()[0]
            print(f"   📺 {series_name}: {count} episodes")
        
        # Check for remaining episodes in content table
        result = conn.execute(text("""
            SELECT COUNT(*) FROM content 
            WHERE content_url ILIKE '%Longstreet-%' 
               OR content_url ILIKE '%CMC%' 
               OR content_url ILIKE '%GS-%'
               OR content_url ILIKE '%Bonanza-%'
        """))
        
        remaining = result.fetchone()[0]
        print(f"   📊 Remaining episodes in content table: {remaining}")

if __name__ == "__main__":
    main() 