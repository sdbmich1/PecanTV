#!/usr/bin/env python3
import psycopg2

# Neon production database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL)

def check_current_longstreet_urls():
    """Check current Longstreet episode URLs"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = (SELECT id FROM content WHERE title = 'Longstreet')
            ORDER BY episode_number
        """)
        
        episodes = cursor.fetchall()
        print(f"Current Longstreet episodes ({len(episodes)} total):")
        
        for episode in episodes:
            print(f"Episode {episode[0]}: {episode[1]}")
            print(f"  URL: {episode[2]}")
            print()
        
    except Exception as e:
        print(f"❌ Error checking Longstreet episodes: {e}")
    finally:
        cursor.close()
        conn.close()

def fix_longstreet_with_known_files():
    """Fix Longstreet episodes with known file names"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Start with the known file pattern and a few examples
    # We know: Longstreet-Beginnings-rev_2p-1080-withCredits.mp4
    # Let's try some common patterns for the first few episodes
    
    known_files = [
        (1, "The Way of the Intercepting Fist", "Longstreet-Beginnings-rev_2p-1080-withCredits.mp4"),
        (2, "A World of Perfect Complicity", "Longstreet-A-World-of-Perfect-Complicity_2p-1080-withCredits.mp4"),
        (3, "The Man Who Killed Himself", "Longstreet-The-Man-Who-Killed-Himself_2p-1080-withCredits.mp4"),
        (4, "So, Who's Fred Hornbeck?", "Longstreet-So-Whos-Fred-Hornbeck_2p-1080-withCredits.mp4"),
        (5, "Elegy in Brass", "Longstreet-Elegy-in-Brass_2p-1080-withCredits.mp4"),
    ]
    
    try:
        for episode_num, title, filename in known_files:
            content_url = f"https://storage.googleapis.com/pecantv_series/longstreet/{filename}"
            
            cursor.execute("""
                UPDATE episodes 
                SET content_url = %s
                WHERE series_id = (SELECT id FROM content WHERE title = 'Longstreet')
                AND episode_number = %s
            """, (content_url, episode_num))
            
            print(f"✅ Updated Longstreet Episode {episode_num}: {title}")
            print(f"   URL: {content_url}")
        
        conn.commit()
        print(f"✅ Updated {len(known_files)} Longstreet episodes with known files")
        print("\n⚠️  Note: Only updated first 5 episodes. Need more file name examples for remaining episodes.")
        
    except Exception as e:
        print(f"❌ Error updating Longstreet episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    print("🔍 Checking current Longstreet episode URLs...")
    check_current_longstreet_urls()
    
    print("\n🔧 Fixing Longstreet episode URLs with known file names...")
    fix_longstreet_with_known_files()
    
    print("\n📝 To fix remaining episodes, please provide more file name examples from GCS.")
    print("   Example format: Longstreet-[Episode-Name]_2p-1080-withCredits.mp4")

if __name__ == "__main__":
    main() 