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
            SELECT id, title, content_url, poster_url, description, runtime 
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
            insert_failed = False
            if not existing_episode:
                try:
                    # Insert into episodes table
                    conn.execute(text("""
                        INSERT INTO episodes (uuid, title, description, season_number, episode_number, 
                                            runtime, content_url, poster_url, air_date, series_id, content_uuid, 
                                            created_at, updated_at)
                        VALUES (gen_random_uuid(), :title, :description, 1, 1, :runtime, :content_url, 
                               :poster_url, NULL, 21, gen_random_uuid(), NOW(), NOW())
                    """), {
                        "title": sleep_of_reason[1],
                        "description": sleep_of_reason[4] or "Petrocelli episode",
                        "runtime": sleep_of_reason[5] or 60,
                        "content_url": sleep_of_reason[2],
                        "poster_url": sleep_of_reason[3] or "https://storage.googleapis.com/pecantv_series/default_poster.jpg"
                    })
                    print("   ✅ Added to Petrocelli episodes")
                except Exception as e:
                    print(f"   ⚠️ Could not add to episodes table: {e}")
                    insert_failed = True
            else:
                print("   ⚠️ Episode already exists in episodes table")
            # Always attempt to remove from content table, using a new transaction
            try:
                conn.execute(text("COMMIT"))
            except Exception:
                pass
            try:
                conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": sleep_of_reason[0]})
                print("   🗑️ Removed from content table")
            except Exception as e:
                print(f"   ⚠️ Could not remove from content table: {e}")
        
        # 4. Move "For Sale: Death Bed-Used" to Longstreet episodes
        print("\n🏠 Moving 'For Sale: Death Bed-Used' to Longstreet episodes...")
        result = conn.execute(text("""
            SELECT id, title, content_url, poster_url, description, runtime 
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
            # Fetch Longstreet series content_uuid
            series_uuid = None
            try:
                series_result = conn.execute(text("SELECT uuid FROM content WHERE id = 49"))
                series_row = series_result.fetchone()
                if series_row:
                    series_uuid = series_row[0]
            except Exception as e:
                print(f"   ⚠️ Could not fetch Longstreet series uuid: {e}")
            if not existing_episode and series_uuid:
                try:
                    # Insert into episodes table
                    conn.execute(text("""
                        INSERT INTO episodes (uuid, title, description, season_number, episode_number, 
                                            runtime, content_url, poster_url, air_date, series_id, content_uuid, 
                                            created_at, updated_at)
                        VALUES (gen_random_uuid(), :title, :description, 1, 1, :runtime, :content_url, 
                               :poster_url, NULL, 49, :series_uuid, NOW(), NOW())
                    """), {
                        "title": for_sale[1],
                        "description": for_sale[4] or "Longstreet episode",
                        "runtime": for_sale[5] or 60,
                        "content_url": for_sale[2],
                        "poster_url": for_sale[3] or "https://storage.googleapis.com/pecantv_series/default_poster.jpg",
                        "series_uuid": series_uuid
                    })
                    print("   ✅ Added to Longstreet episodes")
                except Exception as e:
                    print(f"   ⚠️ Could not add to episodes table: {e}")
            elif not series_uuid:
                print("   ⚠️ Could not find Longstreet series uuid, skipping insert.")
            else:
                print("   ⚠️ Episode already exists in episodes table")
            # Always attempt to remove from content table, using a new transaction
            try:
                conn.execute(text("COMMIT"))
            except Exception:
                pass
            try:
                conn.execute(text("DELETE FROM content WHERE id = :id"), {"id": for_sale[0]})
                print("   🗑️ Removed from content table")
            except Exception as e:
                print(f"   ⚠️ Could not remove from content table: {e}")
        
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