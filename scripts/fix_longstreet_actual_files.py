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

def update_longstreet_episode(episode_number, actual_filename):
    """Update a specific Longstreet episode with the actual filename"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        content_url = f"https://storage.googleapis.com/pecantv_series/longstreet/{actual_filename}"
        
        cursor.execute("""
            UPDATE episodes 
            SET content_url = %s
            WHERE series_id = (SELECT id FROM content WHERE title = 'Longstreet')
            AND episode_number = %s
        """, (content_url, episode_number))
        
        if cursor.rowcount > 0:
            print(f"✅ Updated Longstreet Episode {episode_number}")
            print(f"   URL: {content_url}")
        else:
            print(f"❌ Episode {episode_number} not found")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error updating episode {episode_number}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    print("🔍 Checking current Longstreet episode URLs...")
    check_current_longstreet_urls()
    
    print("📝 Please provide the actual filenames for Longstreet episodes.")
    print("   Example: Longstreet-Beginnings-rev_2p-1080-withCredits.mp4")
    print("   Enter 'done' when finished.")
    
    while True:
        try:
            user_input = input("\nEnter episode number and filename (e.g., '1 Longstreet-Beginnings-rev_2p-1080-withCredits.mp4'): ").strip()
            
            if user_input.lower() == 'done':
                break
            
            if ' ' not in user_input:
                print("❌ Please enter both episode number and filename separated by space")
                continue
            
            episode_num_str, filename = user_input.split(' ', 1)
            
            try:
                episode_num = int(episode_num_str)
                update_longstreet_episode(episode_num, filename)
            except ValueError:
                print("❌ Episode number must be a number")
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Longstreet episode updates completed!")

if __name__ == "__main__":
    main() 