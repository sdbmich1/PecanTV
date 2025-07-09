#!/usr/bin/env python3
"""
Fix remaining duplicate and misclassified content issues.
"""

import os
from sqlalchemy import create_engine, text
from datetime import datetime

# Database configuration
DATABASE_URL = 'postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require'

def fix_remaining_issues():
    """Fix remaining duplicate and misclassified content."""
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    try:
        print("🔧 Fixing remaining content issues...")
        
        # 1. Remove duplicate "Brother from Another Planet" films
        print("\n📺 Removing duplicate Brother from Another Planet films...")
        result = conn.execute(text("""
            SELECT id, title FROM content 
            WHERE type = 'FILM' AND title ILIKE '%brother from another planet%'
            ORDER BY id
        """))
        brother_films = result.fetchall()
        
        if len(brother_films) > 1:
            # Keep the first one, remove the rest
            for film in brother_films[1:]:
                print(f"   Removing duplicate: {film[1]} (ID: {film[0]})")
                conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": film[0]})
        
        # 2. Remove "Lone Ranger" film (episodes are correctly in episodes table)
        print("\n🤠 Removing Lone Ranger film (episodes are in episodes table)...")
        result = conn.execute(text("""
            SELECT id, title FROM content 
            WHERE type = 'FILM' AND title ILIKE '%lone ranger%'
        """))
        lone_ranger_films = result.fetchall()
        
        for film in lone_ranger_films:
            print(f"   Removing film: {film[1]} (ID: {film[0]})")
            conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": film[0]})
        
        # 3. Move "The Sleep of Reason" to Petrocelli episodes
        print("\n👨‍⚖️ Moving 'The Sleep of Reason' to Petrocelli episodes...")
        result = conn.execute(text("""
            SELECT id, title, contentURL, posterURL, description, runtime 
            FROM content 
            WHERE type = 'FILM' AND title ILIKE '%sleep of reason%'
        """))
        sleep_of_reason = result.fetchone()
        
        if sleep_of_reason:
            print(f"   Moving: {sleep_of_reason[1]} (ID: {sleep_of_reason[0]})")
            
            # Check if episode already exists in episodes table
            result = conn.execute(text("""
                SELECT id FROM episodes 
                WHERE title ILIKE '%sleep of reason%' AND series_id = 21
            """))
            existing_episode = result.fetchone()
            
            if not existing_episode:
                # Insert into episodes table
                conn.execute(text("""
                    INSERT INTO episodes (uuid, title, description, seasonNumber, episodeNumber, 
                                        runtime, contentURL, posterURL, airDate, seriesId, contentUuid, 
                                        createdAt, updatedAt)
                    VALUES (gen_random_uuid(), :title, :description, 1, 1, :runtime, :contentURL, 
                           :posterURL, NULL, 21, gen_random_uuid(), NOW(), NOW())
                """), {
                    "title": sleep_of_reason[1],
                    "description": sleep_of_reason[3] or "Petrocelli episode",
                    "runtime": sleep_of_reason[5] or 60,
                    "contentURL": sleep_of_reason[2],
                    "posterURL": sleep_of_reason[4] or "https://storage.googleapis.com/pecantv_series/default_poster.jpg"
                })
                print("   ✅ Added to Petrocelli episodes")
            else:
                print("   ⚠️ Episode already exists in episodes table")
            
            # Remove from content table
            conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": sleep_of_reason[0]})
        
        # 4. Move "For Sale: Death Bed-Used" to Longstreet episodes
        print("\n🏠 Moving 'For Sale: Death Bed-Used' to Longstreet episodes...")
        result = conn.execute(text("""
            SELECT id, title, contentURL, posterURL, description, runtime 
            FROM content 
            WHERE type = 'FILM' AND title ILIKE '%for sale%'
        """))
        for_sale = result.fetchone()
        
        if for_sale:
            print(f"   Moving: {for_sale[1]} (ID: {for_sale[0]})")
            
            # Check if episode already exists in episodes table
            result = conn.execute(text("""
                SELECT id FROM episodes 
                WHERE title ILIKE '%for sale%' AND series_id = 49
            """))
            existing_episode = result.fetchone()
            
            if not existing_episode:
                # Insert into episodes table
                conn.execute(text("""
                    INSERT INTO episodes (uuid, title, description, seasonNumber, episodeNumber, 
                                        runtime, contentURL, posterURL, airDate, seriesId, contentUuid, 
                                        createdAt, updatedAt)
                    VALUES (gen_random_uuid(), :title, :description, 1, 1, :runtime, :contentURL, 
                           :posterURL, NULL, 49, gen_random_uuid(), NOW(), NOW())
                """), {
                    "title": for_sale[1],
                    "description": for_sale[3] or "Longstreet episode",
                    "runtime": for_sale[5] or 60,
                    "contentURL": for_sale[2],
                    "posterURL": for_sale[4] or "https://storage.googleapis.com/pecantv_series/default_poster.jpg"
                })
                print("   ✅ Added to Longstreet episodes")
            else:
                print("   ⚠️ Episode already exists in episodes table")
            
            # Remove from content table
            conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": for_sale[0]})
        
        # Commit all changes
        conn.commit()
        print("\n✅ All fixes completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_remaining_issues() 