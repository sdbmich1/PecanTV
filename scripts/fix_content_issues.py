#!/usr/bin/env python3
"""
Script to fix content issues:
1. Fix Longstreet episode URLs to use correct file names
2. Fix Dragnet episode URLs to use correct file names
3. Remove duplicate Petrocelli episode entries from content table
4. Remove duplicate Count of Monte Cristo episode entries from content table
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

def fix_longstreet_urls():
    """Fix Longstreet episode URLs to use correct file names."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing Longstreet Episode URLs")
        print("=" * 40)
        
        # Get Longstreet series ID
        cur.execute("SELECT id FROM content WHERE title = 'Longstreet' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Longstreet series not found")
            return
        series_id = series_record[0]
        print(f"✅ Found Longstreet series (ID: {series_id})")
        
        # Map of episode numbers to correct file names
        episode_file_map = {
            1: "Longstreet-I-See-Said-the-Blind-Man_2p-1080-withCredits.mp4",
            2: "Longstreet-Beginnings_2p-1080-withCredits.mp4",
            3: "Longstreet-Eye-of-the-Storm_2p-1080-withCredits.mp4",
            4: "Longstreet-Anatomy-of-a-Mayday_2p-1080-withCredits.mp4",
            5: "Longstreet-Elegy-in-Brass_2p-1080-withCredits.mp4",
            6: "Longstreet-A-World-of-Perfect-Complicity_2p-1080-withCredits.mp4"
        }
        
        updated = 0
        for episode_num, filename in episode_file_map.items():
            # Update the episode URL
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (
                f"https://storage.googleapis.com/pecantv_series/longstreet/{filename}",
                datetime.now(timezone.utc),
                series_id,
                episode_num
            ))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated Episode {episode_num}: {filename}")
                updated += 1
            else:
                print(f"  ⚠️  Episode {episode_num} not found")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Longstreet episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fix_dragnet_urls():
    """Fix Dragnet episode URLs to use correct file names."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Fixing Dragnet Episode URLs")
        print("=" * 40)
        
        # Get Dragnet series ID
        cur.execute("SELECT id FROM content WHERE title = 'Dragnet' AND type = 'SERIES'")
        series_record = cur.fetchone()
        if not series_record:
            print("❌ Dragnet series not found")
            return
        series_id = series_record[0]
        print(f"✅ Found Dragnet series (ID: {series_id})")
        
        # Map of episode numbers to correct file names (only for episodes that exist)
        episode_file_map = {
            2: "Dragnet2_2p-1080-wCredits.mp4",
            4: "Dragnet4_2p-1080-wCredits.mp4",
            5: "Dragnet5_2p-1080-wCredits.mp4",
            6: "Dragnet6_2p-1080-wCredits.mp4",
            7: "Dragnet7_2p-1080-wCredits.mp4",
            8: "Dragnet8_2p-1080-wCredits.mp4",
            9: "Dragnet9_2p-1080-wCredits.mp4",
            10: "Dragnet10_2p-1080-wCredits.mp4",
            11: "Dragnet11_2p-1080-wCredits.mp4",
            12: "Dragnet12_2p-1080-wCredits.mp4",
            13: "Dragnet13_2p-1080-wCredits.mp4",
            14: "Dragnet14_2p-1080-wCredits.mp4",
            15: "Dragnet15_2p-1080-wCredits.mp4"
        }
        
        updated = 0
        for episode_num, filename in episode_file_map.items():
            # Update the episode URL
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, updated_at = %s
                WHERE series_id = %s AND episode_number = %s
            """, (
                f"https://storage.googleapis.com/pecantv_series/dragnet/{filename}",
                datetime.now(timezone.utc),
                series_id,
                episode_num
            ))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated Episode {episode_num}: {filename}")
                updated += 1
            else:
                print(f"  ⚠️  Episode {episode_num} not found")
        
        # Note about missing episodes
        print(f"  ℹ️  Note: Dragnet Episodes 1 and 3 are missing from cloud storage")
        
        conn.commit()
        print(f"\n✅ Updated {updated} Dragnet episodes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def remove_duplicate_petrocelli_entries():
    """Remove duplicate Petrocelli episode entries from content table."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🎬 Removing Duplicate Petrocelli Episode Entries")
        print("=" * 50)
        
        # List of Petrocelli episode titles that should be removed from content table
        duplicate_titles = [
            "Too Many Alibis",
            "Four the Hard Way",
            "Once Upon a Victim"
        ]
        
        removed = 0
        for title in duplicate_titles:
            # Check if this title exists in content table
            cur.execute("SELECT id, type FROM content WHERE title = %s", (title,))
            content_record = cur.fetchone()
            
            if content_record:
                content_id, content_type = content_record
                print(f"  Found duplicate: {title} (ID: {content_id}, Type: {content_type})")
                
                # Delete the duplicate entry
                cur.execute("DELETE FROM content WHERE id = %s", (content_id,))
                
                if cur.rowcount > 0:
                    print(f"  ✅ Removed duplicate: {title}")
                    removed += 1
                else:
                    print(f"  ⚠️  Failed to remove: {title}")
            else:
                print(f"  ℹ️  No duplicate found for: {title}")
        
        conn.commit()
        print(f"\n✅ Removed {removed} duplicate Petrocelli episode entries")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def remove_duplicate_monte_cristo_entries():
    """Remove duplicate Count of Monte Cristo episode entries from content table."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("\n🎬 Removing Duplicate Count of Monte Cristo Episode Entries")
        print("=" * 60)
        
        # List of Count of Monte Cristo episode titles that should be removed from content table
        duplicate_titles = [
            "The Texas Affair",
            "A Toy for the Infanta", 
            "Flight to Carais",
            "Albania",
            "The Devil's Emissary",
            "Sicily",
            "Monaco"
        ]
        
        removed = 0
        for title in duplicate_titles:
            # Check if this title exists in content table
            cur.execute("SELECT id, type FROM content WHERE title = %s", (title,))
            content_record = cur.fetchone()
            
            if content_record:
                content_id, content_type = content_record
                print(f"  Found duplicate: {title} (ID: {content_id}, Type: {content_type})")
                
                # Delete the duplicate entry
                cur.execute("DELETE FROM content WHERE id = %s", (content_id,))
                
                if cur.rowcount > 0:
                    print(f"  ✅ Removed duplicate: {title}")
                    removed += 1
                else:
                    print(f"  ⚠️  Failed to remove: {title}")
            else:
                print(f"  ℹ️  No duplicate found for: {title}")
        
        conn.commit()
        print(f"\n✅ Removed {removed} duplicate Count of Monte Cristo episode entries")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Run all fixes."""
    print("🔧 Fixing Content Issues")
    print("=" * 30)
    
    fix_longstreet_urls()
    fix_dragnet_urls()
    remove_duplicate_petrocelli_entries()
    remove_duplicate_monte_cristo_entries()
    
    print("\n✅ All fixes completed!")

if __name__ == "__main__":
    main() 