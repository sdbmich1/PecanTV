#!/usr/bin/env python3
"""
Script to restore Bonanza and Ghost Squad episodes with full metadata from Wurl files
"""

import psycopg2
import pandas as pd
import glob
from datetime import datetime, timezone

def get_episode_metadata():
    """Extract episode metadata from Wurl files."""
    print("🔍 Extracting episode metadata from Wurl files...")
    
    # Find Wurl metadata files
    wurl_files = []
    for pattern in [
        "Wurl - File Upload Metadata_Version 7.0.*.xlsx",
        "Wurl - File Upload Metadata_Version 7.0.*.csv",
        "Wurl-File-Upload-Metadata_Version-7.0.*.xlsx"
    ]:
        wurl_files.extend(glob.glob(pattern))
    
    bonanza_episodes = []
    ghost_squad_episodes = []
    
    for file in sorted(wurl_files):
        try:
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, encoding='utf-8')
            
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                
                # Bonanza episodes
                bonanza_df = df[df['Series Name'].str.strip().str.lower() == 'bonanza']
                for _, row in bonanza_df.iterrows():
                    title = str(row.get('Title', '')).strip()
                    video_filename = str(row.get('Video Filename', '')).strip()
                    artwork_filename = str(row.get('Artwork Filename', '')).strip()
                    
                    try:
                        season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                    except (ValueError, TypeError):
                        season = 1
                    
                    try:
                        episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                    except (ValueError, TypeError):
                        episode = 1
                    
                    episode_info = {
                        'title': title,
                        'season': season,
                        'episode': episode,
                        'video_filename': video_filename if video_filename != 'nan' else '',
                        'artwork_filename': artwork_filename if artwork_filename != 'nan' else '',
                        'description': str(row.get('Description', '')).strip(),
                        'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60
                    }
                    
                    # Only add if not already present (avoid duplicates)
                    key = (season, episode)
                    if not any(ep['season'] == season and ep['episode'] == episode for ep in bonanza_episodes):
                        bonanza_episodes.append(episode_info)
                
                # Ghost Squad episodes
                ghost_squad_df = df[df['Series Name'].str.strip().str.lower() == 'ghost squad']
                for _, row in ghost_squad_df.iterrows():
                    title = str(row.get('Title', '')).strip()
                    video_filename = str(row.get('Video Filename', '')).strip()
                    artwork_filename = str(row.get('Artwork Filename', '')).strip()
                    
                    try:
                        season = int(row.get('Season Number', 1)) if pd.notna(row.get('Season Number')) else 1
                    except (ValueError, TypeError):
                        season = 1
                    
                    try:
                        episode = int(row.get('Episode Number', 1)) if pd.notna(row.get('Episode Number')) else 1
                    except (ValueError, TypeError):
                        episode = 1
                    
                    episode_info = {
                        'title': title,
                        'season': season,
                        'episode': episode,
                        'video_filename': video_filename if video_filename != 'nan' else '',
                        'artwork_filename': artwork_filename if artwork_filename != 'nan' else '',
                        'description': str(row.get('Description', '')).strip(),
                        'runtime': int(row.get('Runtime', 60)) if pd.notna(row.get('Runtime')) else 60
                    }
                    
                    # Only add if not already present (avoid duplicates)
                    key = (season, episode)
                    if not any(ep['season'] == season and ep['episode'] == episode for ep in ghost_squad_episodes):
                        ghost_squad_episodes.append(episode_info)
        
        except Exception as e:
            print(f"  ⚠️  Error reading {file}: {e}")
    
    # Sort episodes
    bonanza_episodes.sort(key=lambda x: (x['season'], x['episode']))
    ghost_squad_episodes.sort(key=lambda x: (x['season'], x['episode']))
    
    return bonanza_episodes, ghost_squad_episodes

def restore_episodes():
    """Restore episodes to the database."""
    # Database connection
    conn = psycopg2.connect(
        host='localhost',
        database='pecantv',
        user='postgres',
        password='postgres',
        port='5433'
    )
    
    cursor = conn.cursor()
    
    # Get episode metadata
    bonanza_episodes, ghost_squad_episodes = get_episode_metadata()
    
    print(f"\n📊 Found {len(bonanza_episodes)} Bonanza episodes and {len(ghost_squad_episodes)} Ghost Squad episodes")
    
    # Find series IDs
    cursor.execute("SELECT id FROM content WHERE title = 'Bonanza' AND type = 'SERIES'")
    bonanza_series_id = cursor.fetchone()
    if not bonanza_series_id:
        print("❌ Bonanza series not found in database!")
        return
    bonanza_series_id = bonanza_series_id[0]
    
    cursor.execute("SELECT id FROM content WHERE title = 'Ghost Squad' AND type = 'SERIES'")
    ghost_squad_series_id = cursor.fetchone()
    if not ghost_squad_series_id:
        print("❌ Ghost Squad series not found in database!")
        return
    ghost_squad_series_id = ghost_squad_series_id[0]
    
    print(f"✅ Bonanza series ID: {bonanza_series_id}")
    print(f"✅ Ghost Squad series ID: {ghost_squad_series_id}")
    
    # Clear existing episodes for both series
    print("\n🗑️  Clearing existing episodes...")
    cursor.execute("DELETE FROM episodes WHERE series_id = %s", (bonanza_series_id,))
    bonanza_deleted = cursor.rowcount
    cursor.execute("DELETE FROM episodes WHERE series_id = %s", (ghost_squad_series_id,))
    ghost_squad_deleted = cursor.rowcount
    
    print(f"   Deleted {bonanza_deleted} existing Bonanza episodes")
    print(f"   Deleted {ghost_squad_deleted} existing Ghost Squad episodes")
    
    # Insert Bonanza episodes
    print(f"\n🎬 Inserting {len(bonanza_episodes)} Bonanza episodes...")
    for i, ep in enumerate(bonanza_episodes, 1):
        # Create video URL
        video_url = f"https://storage.googleapis.com/pecantv_series/bonanza/{ep['video_filename']}"
        
        # Create thumbnail URL
        thumbnail_url = f"https://storage.googleapis.com/pecantv_title_images/{ep['artwork_filename']}"
        
        cursor.execute("""
            INSERT INTO episodes (
                series_id, season_number, episode_number, title, description, 
                content_url, thumbnail_url, runtime, air_date, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            bonanza_series_id,
            ep['season'],
            ep['episode'],
            ep['title'],
            ep['description'],
            video_url,
            thumbnail_url,
            ep['runtime'],
            None,  # air_date
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        print(f"   {i:2d}. S{ep['season']:02d}E{ep['episode']:02d} - {ep['title']}")
        print(f"       Video: {ep['video_filename']}")
        print(f"       Thumbnail: {ep['artwork_filename']}")
    
    # Insert Ghost Squad episodes
    print(f"\n👻 Inserting {len(ghost_squad_episodes)} Ghost Squad episodes...")
    for i, ep in enumerate(ghost_squad_episodes, 1):
        # Create video URL
        video_url = f"https://storage.googleapis.com/pecantv_series/ghost_squad/{ep['video_filename']}"
        
        # Create thumbnail URL
        thumbnail_url = f"https://storage.googleapis.com/pecantv_title_images/{ep['artwork_filename']}"
        
        cursor.execute("""
            INSERT INTO episodes (
                series_id, season_number, episode_number, title, description, 
                content_url, thumbnail_url, runtime, air_date, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            ghost_squad_series_id,
            ep['season'],
            ep['episode'],
            ep['title'],
            ep['description'],
            video_url,
            thumbnail_url,
            ep['runtime'],
            None,  # air_date
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        print(f"   {i:2d}. S{ep['season']:02d}E{ep['episode']:02d} - {ep['title']}")
        print(f"       Video: {ep['video_filename']}")
        print(f"       Thumbnail: {ep['artwork_filename']}")
    
    # Commit changes
    conn.commit()
    
    # Verify the insertions
    print(f"\n✅ VERIFICATION")
    print("=" * 50)
    
    cursor.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (bonanza_series_id,))
    bonanza_count = cursor.fetchone()[0]
    print(f"🎬 Bonanza episodes in database: {bonanza_count}")
    
    cursor.execute("SELECT COUNT(*) FROM episodes WHERE series_id = %s", (ghost_squad_series_id,))
    ghost_squad_count = cursor.fetchone()[0]
    print(f"👻 Ghost Squad episodes in database: {ghost_squad_count}")
    
    cursor.close()
    conn.close()
    
    print(f"\n🎉 SUCCESS! Restored {bonanza_count} Bonanza episodes and {ghost_squad_count} Ghost Squad episodes")
    print("The episodes should now be available in your app!")

if __name__ == "__main__":
    restore_episodes() 