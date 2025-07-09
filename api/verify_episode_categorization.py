#!/usr/bin/env python3
"""
Verify episode categorization
"""

import os
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def main():
    print("🔍 Verifying episode categorization...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check episode counts for each series
        series_names = {49: 'Longstreet', 72: 'Count of Monte Cristo', 78: 'Bonanza', 62: 'Ghost Squad'}
        
        print("\n📺 Episode counts by series:")
        for series_id, series_name in series_names.items():
            result = conn.execute(text("""
                SELECT COUNT(*) FROM episodes WHERE series_id = :series_id
            """), {'series_id': series_id})
            
            count = result.fetchone()[0]
            print(f"   {series_name}: {count} episodes")
        
        # Check for remaining episodes in content table
        result = conn.execute(text("""
            SELECT COUNT(*) FROM content 
            WHERE content_url ILIKE '%Longstreet-%' 
               OR content_url ILIKE '%CMC%' 
               OR content_url ILIKE '%GS-%'
               OR content_url ILIKE '%Bonanza-%'
        """))
        
        remaining = result.fetchone()[0]
        print(f"\n📊 Remaining episodes in content table: {remaining}")
        
        if remaining == 0:
            print("✅ All episodes successfully moved to episodes table!")
        else:
            print("⚠️  Some episodes still remain in content table")
        
        # Check specific episodes mentioned by user
        print(f"\n🎯 Checking specific episodes:")
        
        # Check "Sad Songs" (Longstreet)
        result = conn.execute(text("""
            SELECT series_id, title FROM episodes 
            WHERE title ILIKE '%sad songs%'
        """))
        row = result.fetchone()
        if row:
            series_name = series_names.get(row[0], f"Series {row[0]}")
            print(f"   ✅ Sad Songs and Other Conversations: {series_name}")
        else:
            print(f"   ❌ Sad Songs and Other Conversations: Not found in episodes")
        
        # Check "Day of Reckoning" (Bonanza)
        result = conn.execute(text("""
            SELECT series_id, title FROM episodes 
            WHERE title ILIKE '%day of reckoning%'
        """))
        row = result.fetchone()
        if row:
            series_name = series_names.get(row[0], f"Series {row[0]}")
            print(f"   ✅ Day of Reckoning: {series_name}")
        else:
            print(f"   ❌ Day of Reckoning: Not found in episodes")
        
        # Check "Andorra" (CMC)
        result = conn.execute(text("""
            SELECT series_id, title FROM episodes 
            WHERE title ILIKE '%andorra%'
        """))
        row = result.fetchone()
        if row:
            series_name = series_names.get(row[0], f"Series {row[0]}")
            print(f"   ✅ Andorra: {series_name}")
        else:
            print(f"   ❌ Andorra: Not found in episodes")
        
        # Check "The Duel" (CMC)
        result = conn.execute(text("""
            SELECT series_id, title FROM episodes 
            WHERE title ILIKE '%duel%'
        """))
        row = result.fetchone()
        if row:
            series_name = series_names.get(row[0], f"Series {row[0]}")
            print(f"   ✅ The Duel: {series_name}")
        else:
            print(f"   ❌ The Duel: Not found in episodes")

if __name__ == "__main__":
    main() 