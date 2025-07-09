#!/usr/bin/env python3
"""
Fix final remaining misclassified episodes and duplicate series entries.
"""

import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Database configuration
DATABASE_URL = 'postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require'

def fix_final_issues():
    """Fix final remaining misclassified episodes and duplicate series."""
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    try:
        print("🔧 Fixing final remaining issues...")
        
        # 1. Move Petrocelli episodes from films to episodes table
        petrocelli_episodes = [
            "The Shadow of Fear",
            "The Night Visitor", 
            "The Face of Evil"
        ]
        
        print("\n👨‍⚖️ Moving Petrocelli episodes from films to episodes table...")
        
        # Fetch Petrocelli series content_uuid
        series_uuid = None
        try:
            series_result = conn.execute(text("SELECT uuid FROM content WHERE id = 21"))
            series_row = series_result.fetchone()
            if series_row:
                series_uuid = series_row[0]
                print(f"   Found Petrocelli series UUID: {series_uuid}")
        except Exception as e:
            print(f"   ❌ Could not fetch Petrocelli series uuid: {e}")
            return
        
        for episode_title in petrocelli_episodes:
            print(f"\n   Processing: {episode_title}")
            
            # Check if it exists in content table as a film
            result = conn.execute(text("""
                SELECT id, title, content_url, poster_url, description, runtime 
                FROM content 
                WHERE type = 'FILM' AND title ILIKE :title
            """), {"title": f"%{episode_title}%"})
            
            film_entry = result.fetchone()
            
            if film_entry:
                print(f"     Found in films: {film_entry[1]} (ID: {film_entry[0]})")
                
                # Check if episode already exists in episodes table
                result = conn.execute(text("""
                    SELECT id FROM episodes 
                    WHERE title ILIKE :title AND series_id = 21
                """), {"title": f"%{episode_title}%"})
                
                existing_episode = result.fetchone()
                
                if not existing_episode:
                    try:
                        # Insert into episodes table
                        conn.execute(text("""
                            INSERT INTO episodes (uuid, title, description, season_number, episode_number, 
                                                runtime, content_url, poster_url, air_date, series_id, content_uuid, 
                                                created_at, updated_at)
                            VALUES (gen_random_uuid(), :title, :description, 1, 1, :runtime, :content_url, 
                                   :poster_url, NULL, 21, :series_uuid, NOW(), NOW())
                        """), {
                            "title": film_entry[1],
                            "description": film_entry[4] or "Petrocelli episode",
                            "runtime": film_entry[5] or 60,
                            "content_url": film_entry[2],
                            "poster_url": film_entry[3] or "https://storage.googleapis.com/pecantv_series/default_poster.jpg",
                            "series_uuid": series_uuid
                        })
                        print(f"     ✅ Added to Petrocelli episodes")
                    except Exception as e:
                        print(f"     ⚠️ Could not add to episodes table: {e}")
                else:
                    print(f"     ⚠️ Episode already exists in episodes table")
                
                # Remove from content table
                try:
                    conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": film_entry[0]})
                    print(f"     🗑️ Removed from content table")
                except Exception as e:
                    print(f"     ⚠️ Could not remove from content table: {e}")
            else:
                print(f"     ❌ Not found in films table")
        
        # 2. Remove duplicate Lone Ranger series entries
        print("\n🤠 Removing duplicate Lone Ranger series entries...")
        
        result = conn.execute(text("""
            SELECT id, title, uuid FROM content 
            WHERE type = 'SERIES' AND title ILIKE '%lone ranger%'
            ORDER BY id
        """))
        
        lone_ranger_series = result.fetchall()
        
        if len(lone_ranger_series) > 1:
            print(f"   Found {len(lone_ranger_series)} Lone Ranger series entries")
            
            # Keep the first one, remove the rest
            for series in lone_ranger_series[1:]:
                print(f"   Removing duplicate: {series[1]} (ID: {series[0]}, UUID: {series[2]})")
                try:
                    conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": series[0]})
                    print(f"     ✅ Removed duplicate series")
                except Exception as e:
                    print(f"     ⚠️ Could not remove duplicate series: {e}")
        else:
            print(f"   Found {len(lone_ranger_series)} Lone Ranger series entries (no duplicates)")
        
        # Commit all changes
        conn.commit()
        print("\n✅ All final fixes completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_final_issues() 