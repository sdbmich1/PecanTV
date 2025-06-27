#!/usr/bin/env python3
"""
Script to fix Commando Cody episodes with content URLs and poster URLs from the pecantv_series/commando_cody folder.
"""

import psycopg2
import os
import glob

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def get_commando_cody_files():
    """Get the video and artwork files from the commando_cody folder."""
    folder_path = "pecantv_series/commando_cody"
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return [], []
    
    # Get all files in the folder
    all_files = os.listdir(folder_path)
    print(f"📁 Found {len(all_files)} files in {folder_path}")
    
    # Separate video and artwork files
    video_files = []
    artwork_files = []
    
    for file in all_files:
        file_lower = file.lower()
        if any(ext in file_lower for ext in ['.mp4', '.avi', '.mov', '.mkv']):
            video_files.append(file)
        elif any(ext in file_lower for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            artwork_files.append(file)
    
    print(f"🎥 Video files: {len(video_files)}")
    for file in video_files:
        print(f"  • {file}")
    
    print(f"🖼️  Artwork files: {len(artwork_files)}")
    for file in artwork_files:
        print(f"  • {file}")
    
    return video_files, artwork_files

def update_commando_cody_episodes():
    """Update Commando Cody episodes with correct content URLs and poster URLs."""
    print("🔧 Fixing Commando Cody episodes with file URLs")
    print("=" * 60)
    
    # Get files from the folder
    video_files, artwork_files = get_commando_cody_files()
    
    if not video_files:
        print("❌ No video files found")
        return
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Commando Cody series ID
        cur.execute("""
            SELECT id FROM content 
            WHERE title = 'Commando Cody - Sky Marshal of the Universe' AND type = 'SERIES'
        """)
        result = cur.fetchone()
        
        if not result:
            print("❌ Commando Cody series not found")
            return
        
        series_id = result[0]
        print(f"✅ Found Commando Cody series (ID: {series_id})")
        
        # Get all episodes for this series
        cur.execute("""
            SELECT id, title, content_url, poster_url 
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"📺 Found {len(episodes)} episodes")
        
        updated_count = 0
        
        for ep_id, title, current_content_url, current_poster_url in episodes:
            print(f"\n🔍 Processing: {title}")
            
            # Find matching video file
            matching_video = None
            for video_file in video_files:
                # Check if the video filename matches the episode title
                if any(keyword in video_file.lower() for keyword in title.lower().split()):
                    matching_video = video_file
                    break
            
            # Find matching artwork file
            matching_artwork = None
            for artwork_file in artwork_files:
                # Check if the artwork filename matches the episode title
                if any(keyword in artwork_file.lower() for keyword in title.lower().split()):
                    matching_artwork = artwork_file
                    break
            
            # If no specific match, use the first available files
            if not matching_video and video_files:
                matching_video = video_files[0]  # Use first video file as default
            if not matching_artwork and artwork_files:
                matching_artwork = artwork_files[0]  # Use first artwork file as default
            
            # Update the episode
            new_content_url = f"pecantv_series/commando_cody/{matching_video}" if matching_video else current_content_url
            new_poster_url = f"pecantv_series/commando_cody/{matching_artwork}" if matching_artwork else current_poster_url
            
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, poster_url = %s 
                WHERE id = %s
            """, (new_content_url, new_poster_url, ep_id))
            
            print(f"  ✅ Updated:")
            print(f"     Content URL: {new_content_url}")
            print(f"     Poster URL: {new_poster_url}")
            updated_count += 1
        
        conn.commit()
        print(f"\n🎉 Successfully updated {updated_count} Commando Cody episodes!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_commando_cody_episodes() 