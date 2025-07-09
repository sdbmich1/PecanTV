#!/usr/bin/env python3
"""
Clean up remaining episodes from content table
"""

import os
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def main():
    print("🧹 Cleaning up remaining episodes from content table...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all episodes that need to be removed from content table
        result = conn.execute(text("""
            SELECT id, title, content_url FROM content 
            WHERE content_url ILIKE '%Longstreet-%' 
               OR content_url ILIKE '%CMC%' 
               OR content_url ILIKE '%GS-%'
               OR content_url ILIKE '%Bonanza-%'
            ORDER BY title
        """))
        
        episodes_to_remove = result.fetchall()
        print(f"Found {len(episodes_to_remove)} episodes to remove from content table")
        
        # Remove each episode from content table
        for content_id, title, content_url in episodes_to_remove:
            print(f"🗑️  Removing: {title}")
            
            try:
                conn.execute(text("DELETE FROM content WHERE id = :id"), {'id': content_id})
                print(f"   ✅ Removed from content table")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ All changes committed successfully!")
        
        # Verify the cleanup
        result = conn.execute(text("""
            SELECT COUNT(*) FROM content 
            WHERE content_url ILIKE '%Longstreet-%' 
               OR content_url ILIKE '%CMC%' 
               OR content_url ILIKE '%GS-%'
               OR content_url ILIKE '%Bonanza-%'
        """))
        
        remaining = result.fetchone()[0]
        print(f"📊 Remaining episodes in content table: {remaining}")
        
        if remaining == 0:
            print("🎉 All episodes successfully cleaned up!")
        else:
            print("⚠️  Some episodes may still remain in content table")

if __name__ == "__main__":
    main() 