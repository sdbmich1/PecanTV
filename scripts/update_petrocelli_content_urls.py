#!/usr/bin/env python3
"""
Script to update Petrocelli episodes with content URLs from the found video filenames.
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

# Petrocelli episodes with video filenames found from Dropbox files
PETROCELLI_EPISODES = {
    'Blood Money': 'Petrocelli-Blood-Money_2p-1080-wCredits.mp4',
    'Any Number Can Die': 'Petrocelli-Any-Number-Can-Die_2p-1080-wCredits.mp4',
    'Deadly Journey': 'Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4',
    'Jubilee Jones': 'Petrocelli-Jubilee-Jones_2p-1080-wCredits.mp4',
    'The Night Visitor': 'Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4',
    'To See No Evil': 'Petrocelli-To-See-No-Evil_2p-1080-wCredits.mp4',
    'The Gamblers': 'Petrocelli-The-Gamblers_2p-1080-wCredits.mp4',
    'Terror on Wheels': 'Petrocelli-Terror-on-Wheels_2p-1080-wCredits.mp4',
    'Face of Evil': 'Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4',
    'Too Many Alibis': 'Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4',
    'Survival': 'Petrocelli-Survival_2p-1080-wCredits.mp4',
    'Four the Hard Way': 'Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4',
    'Shadow of Fear': 'Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4',
    'Death Ride': 'Petrocelli-Death-Ride_2p-1080-wCredits.mp4',
    'Five Yards of Trouble': 'Petrocelli-Five-Yard-of-Trouble_2p-1080-wCredits.mp4',
    'A Lonely Victim': 'Petrocelli-A-Lonely-Victim_2p-1080-wCredits.mp4',
    'The Sleep of Reason': 'Petrocelli-The-Sleep-of-Reason_2p-1080-wCredits.mp4'
}

def update_petrocelli_content_urls():
    """Update Petrocelli episodes with content URLs from video filenames."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Updating Petrocelli Episode Content URLs")
        print("=" * 50)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result[0]
        print(f"✅ Found Petrocelli series (ID: {series_id})")
        
        updated_count = 0
        
        for title, video_filename in PETROCELLI_EPISODES.items():
            # Check if episode exists and has empty content_url
            cur.execute("""
                SELECT id, content_url FROM episodes 
                WHERE series_id = %s AND title = %s
            """, (series_id, title))
            
            episode_result = cur.fetchone()
            if episode_result:
                ep_id, current_url = episode_result
                
                if not current_url or current_url.strip() == '':
                    # Construct the content URL
                    content_url = f"https://storage.googleapis.com/pecantv_features/{video_filename}"
                    
                    # Update the episode
                    cur.execute("""
                        UPDATE episodes 
                        SET content_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (content_url, datetime.now(timezone.utc), ep_id))
                    
                    print(f"  ✅ Updated: {title}")
                    print(f"     URL: {content_url}")
                    updated_count += 1
                else:
                    print(f"  ⚠️  Already has URL: {title}")
            else:
                print(f"  ❌ Episode not found: {title}")
        
        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} Petrocelli episodes!")
        
        # Show final status
        print("\n📊 Final Status Check:")
        print("-" * 30)
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN e.content_url IS NULL OR e.content_url = '' THEN 1 END) as missing,
                COUNT(CASE WHEN e.content_url IS NOT NULL AND e.content_url != '' THEN 1 END) as valid
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            WHERE c.title = 'Petrocelli'
        """)
        
        total, missing, valid = cur.fetchone()
        print(f"  Petrocelli: {valid}/{total} episodes have valid URLs")
        
        if missing > 0:
            print(f"  ⚠️  {missing} episodes still missing content URLs")
        else:
            print(f"  ✅ All Petrocelli episodes now have valid content URLs!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_petrocelli_content_urls() 