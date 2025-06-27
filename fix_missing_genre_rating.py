#!/usr/bin/env python3
"""
Script to fix missing genre and rating data for content items.
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

def fix_missing_genre_rating():
    """Fix missing genre and rating data for content items."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔧 Fixing Missing Genre and Rating Data")
        print("=" * 50)
        
        # Get content items with missing genre or rating
        cur.execute("""
            SELECT id, title, type, description, genre_id, rating_id
            FROM content 
            WHERE genre_id IS NULL OR rating_id IS NULL
            ORDER BY title
        """)
        
        items_to_fix = cur.fetchall()
        print(f"Found {len(items_to_fix)} items with missing genre or rating data")
        
        # Default mappings based on content type and title
        default_genre_mappings = {
            # Films - default to Drama
            'FILM': 9,  # Drama
            
            # Series - default to Drama
            'SERIES': 9,  # Drama
        }
        
        # Specific title-based genre mappings
        title_genre_mappings = {
            'petrocelli': 7,  # Crime
            'dragnet': 7,     # Crime
            'lone ranger': 2, # Adventure
            'bonanza': 32,    # Western
            'ghost squad': 1, # Action
            'man with a camera': 20, # Mystery
            'longstreet': 7,  # Crime
            'carnival of souls': 18, # Horror
            'charade': 31,    # Thriller
            'beat the devil': 31, # Thriller
            'captain kidd': 2, # Adventure
            'captain scarlett': 2, # Adventure
            'black brigade': 1, # Action
            'brother from another planet': 26, # Science Fiction
            'beyond christmas': 6, # Comedy
            'a christmas wish': 6, # Comedy
        }
        
        # Default rating mappings
        default_rating_mappings = {
            'FILM': 4,  # TVPG
            'SERIES': 4, # TVPG
        }
        
        # Specific title-based rating mappings
        title_rating_mappings = {
            'carnival of souls': 5,  # TV14
            'charade': 4,            # TVPG
            'beat the devil': 5,     # TV14
            'captain kidd': 4,       # TVPG
            'captain scarlett': 4,   # TVPG
            'black brigade': 5,      # TV14
            'brother from another planet': 4, # TVPG
        }
        
        updated_count = 0
        
        for item_id, title, content_type, description, current_genre_id, current_rating_id in items_to_fix:
            print(f"\nProcessing: {title} (Type: {content_type})")
            
            # Determine genre
            new_genre_id = current_genre_id
            if current_genre_id is None:
                # Check title-based mapping first
                title_lower = title.lower()
                genre_found = False
                
                for key, genre_id in title_genre_mappings.items():
                    if key in title_lower:
                        new_genre_id = genre_id
                        genre_found = True
                        print(f"  → Assigned genre based on title: {key}")
                        break
                
                # Fall back to type-based default
                if not genre_found:
                    new_genre_id = default_genre_mappings.get(content_type, 9)  # Default to Drama
                    print(f"  → Assigned default genre for {content_type}")
            
            # Determine rating
            new_rating_id = current_rating_id
            if current_rating_id is None:
                # Check title-based mapping first
                title_lower = title.lower()
                rating_found = False
                
                for key, rating_id in title_rating_mappings.items():
                    if key in title_lower:
                        new_rating_id = rating_id
                        rating_found = True
                        print(f"  → Assigned rating based on title: {key}")
                        break
                
                # Fall back to type-based default
                if not rating_found:
                    new_rating_id = default_rating_mappings.get(content_type, 4)  # Default to TVPG
                    print(f"  → Assigned default rating for {content_type}")
            
            # Update the database
            if new_genre_id != current_genre_id or new_rating_id != current_rating_id:
                cur.execute("""
                    UPDATE content 
                    SET genre_id = %s, rating_id = %s, updated_at = %s
                    WHERE id = %s
                """, (new_genre_id, new_rating_id, datetime.now(timezone.utc), item_id))
                
                updated_count += 1
                print(f"  ✅ Updated genre_id: {current_genre_id} → {new_genre_id}")
                print(f"  ✅ Updated rating_id: {current_rating_id} → {new_rating_id}")
            else:
                print(f"  ⏭️  No changes needed")
        
        # Commit changes
        conn.commit()
        
        print(f"\n📊 Summary:")
        print(f"  • Items processed: {len(items_to_fix)}")
        print(f"  • Items updated: {updated_count}")
        
        # Verify the fix
        cur.execute("""
            SELECT COUNT(*) 
            FROM content 
            WHERE genre_id IS NULL OR rating_id IS NULL
        """)
        
        remaining_missing = cur.fetchone()[0]
        print(f"  • Items still missing data: {remaining_missing}")
        
        if remaining_missing == 0:
            print("✅ All content now has genre and rating data!")
        else:
            print(f"⚠️  {remaining_missing} items still need manual review")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_missing_genre_rating() 