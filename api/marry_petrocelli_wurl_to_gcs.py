#!/usr/bin/env python3
"""
Script to marry WURL metadata to GCS files for Petrocelli episodes
"""

import os
import sys
import csv
import glob
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import requests

# Load environment variables
load_dotenv()

def get_database_url():
    """
    Get database URL from environment variables.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("📝 Please ensure .env file contains DATABASE_URL")
        sys.exit(1)
    
    # Handle Neon database URL transformation
    if "neon.tech" in database_url:
        parsed = urllib.parse.urlparse(database_url)
        if parsed.scheme == "postgresql":
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
    
    return database_url

def extract_petrocelli_from_wurl():
    """
    Extract all Petrocelli episodes from WURL metadata files
    """
    wurl_files = glob.glob("../Wurl - File Upload Metadata_Version*.csv")
    petrocelli_episodes = []
    
    print(f"🔍 Searching {len(wurl_files)} WURL files for Petrocelli episodes...")
    
    for wurl_file in wurl_files:
        print(f"📄 Processing {os.path.basename(wurl_file)}...")
        
        try:
            with open(wurl_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Check if this is a Petrocelli episode
                    series_name = row.get('Series Name', '').strip()
                    video_filename = row.get('Video Filename', '').strip()
                    title = row.get('Title', '').strip()
                    
                    # Look for Petrocelli in series name or video filename
                    if ('petrocelli' in series_name.lower() or 
                        'petrocelli' in video_filename.lower() or
                        'petrocelli' in title.lower()):
                        
                        episode_data = {
                            'external_id': row.get('External ID', ''),
                            'title': title,
                            'internal_title': row.get('Internal Title', ''),
                            'description': row.get('Description', ''),
                            'short_description': row.get('Short Description', ''),
                            'series_name': series_name,
                            'season_number': row.get('Season Number', ''),
                            'episode_number': row.get('Episode Number', ''),
                            'keywords': row.get('Keywords', ''),
                            'categories': row.get('Categories', ''),
                            'release_date': row.get('Release Date', ''),
                            'video_filename': video_filename,
                            'artwork_filename': row.get('Artwork Filename', ''),
                            'series_artwork_filename': row.get('Series Artwork Filename', ''),
                            'genre_source': row.get('Genre Source', ''),
                            'genre_value': row.get('Genre Value', ''),
                            'rating_source': row.get('Rating Source', ''),
                            'rating_value': row.get('Rating Value', ''),
                            'cut_points': row.get('Cut Points ', ''),
                            'entry_type': row.get('Entry Type', ''),
                            'wurl_file': os.path.basename(wurl_file)
                        }
                        
                        petrocelli_episodes.append(episode_data)
                        print(f"  ✅ Found: {title} (Episode {episode_data['episode_number']}) - {video_filename}")
        
        except Exception as e:
            print(f"  ❌ Error processing {wurl_file}: {e}")
    
    return petrocelli_episodes

def get_current_episodes_from_db():
    """
    Get current Petrocelli episodes from database
    """
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        query = text("""
            SELECT episode_number, title, content_url, poster_url, description
            FROM episodes 
            WHERE series_id = 21 
            ORDER BY episode_number
        """)
        
        result = conn.execute(query)
        episodes = []
        
        for row in result:
            episodes.append({
                'episode_number': row.episode_number,
                'title': row.title,
                'content_url': row.content_url,
                'poster_url': row.poster_url,
                'description': row.description
            })
    
    return episodes

def match_wurl_to_gcs(wurl_episodes, db_episodes):
    """
    Match WURL episodes to GCS files and database episodes
    """
    matches = []
    
    print(f"\n🔗 Matching {len(wurl_episodes)} WURL episodes to {len(db_episodes)} database episodes...")
    
    for wurl_ep in wurl_episodes:
        wurl_filename = wurl_ep['video_filename']
        wurl_episode_num = wurl_ep['episode_number']
        wurl_title = wurl_ep['title']
        
        # Try to match by episode number first
        db_match = None
        for db_ep in db_episodes:
            if str(db_ep['episode_number']) == str(wurl_episode_num):
                db_match = db_ep
                break
        
        # If no match by episode number, try to match by filename
        if not db_match:
            for db_ep in db_episodes:
                db_content_url = db_ep['content_url']
                if wurl_filename in db_content_url:
                    db_match = db_ep
                    break
        
        match_info = {
            'wurl_episode': wurl_ep,
            'db_episode': db_match,
            'matched': db_match is not None,
            'match_method': 'episode_number' if db_match and str(db_match['episode_number']) == str(wurl_episode_num) else 'filename' if db_match else 'none'
        }
        
        matches.append(match_info)
        
        if db_match:
            print(f"  ✅ Matched: {wurl_title} (WURL Ep {wurl_episode_num}) -> DB Ep {db_match['episode_number']} ({db_match['title']})")
        else:
            print(f"  ❌ No match: {wurl_title} (WURL Ep {wurl_episode_num}) - {wurl_filename}")
    
    return matches

def update_episodes_with_wurl_data(matches):
    """
    Update database episodes with WURL metadata
    """
    engine = create_engine(get_database_url())
    
    updated_count = 0
    
    with engine.connect() as conn:
        for match in matches:
            if not match['matched']:
                continue
                
            wurl_ep = match['wurl_episode']
            db_ep = match['db_episode']
            
            # Update episode with WURL data
            update_query = text("""
                UPDATE episodes 
                SET 
                    description = :description,
                    updated_at = :updated_at
                WHERE series_id = 21 AND episode_number = :episode_number
            """)
            
            try:
                conn.execute(update_query, {
                    'description': wurl_ep['description'] or wurl_ep['short_description'] or db_ep['description'],
                    'updated_at': datetime.utcnow(),
                    'episode_number': db_ep['episode_number']
                })
                
                updated_count += 1
                print(f"  ✅ Updated episode {db_ep['episode_number']}: {db_ep['title']}")
                
            except Exception as e:
                print(f"  ❌ Error updating episode {db_ep['episode_number']}: {e}")
        
        conn.commit()
    
    return updated_count

def check_gcs_files(wurl_episodes):
    """
    Check if each WURL episode's video file exists in GCS
    """
    gcs_base = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"
    results = []
    print("\n🔍 Checking GCS file existence for each WURL episode...")
    for ep in wurl_episodes:
        filename = ep['video_filename']
        if not filename:
            results.append((ep, False, "No filename in WURL metadata"))
            continue
        url = gcs_base + filename
        try:
            r = requests.head(url, timeout=5)
            exists = r.status_code == 200
            results.append((ep, exists, url))
            if exists:
                print(f"  ✅ FOUND: {filename}")
            else:
                print(f"  ❌ MISSING: {filename}")
        except Exception as e:
            results.append((ep, False, str(e)))
            print(f"  ❌ ERROR: {filename} ({e})")
    return results

def main():
    print("🎬 Petrocelli WURL to GCS Marriage Script")
    print("=" * 50)
    
    # Extract Petrocelli episodes from WURL files
    wurl_episodes = extract_petrocelli_from_wurl()
    
    if not wurl_episodes:
        print("❌ No Petrocelli episodes found in WURL files")
        return
    
    print(f"\n📊 Found {len(wurl_episodes)} Petrocelli episodes in WURL files:")
    for ep in wurl_episodes:
        print(f"  • Episode {ep['episode_number']}: {ep['title']} ({ep['video_filename']})")
    
    # Get current episodes from database
    db_episodes = get_current_episodes_from_db()
    print(f"\n📊 Found {len(db_episodes)} Petrocelli episodes in database")
    
    # Match WURL episodes to GCS files
    matches = match_wurl_to_gcs(wurl_episodes, db_episodes)
    
    # Count matches
    matched_count = sum(1 for m in matches if m['matched'])
    unmatched_count = len(matches) - matched_count
    
    print(f"\n📈 Matching Results:")
    print(f"  ✅ Matched: {matched_count}")
    print(f"  ❌ Unmatched: {unmatched_count}")
    
    # Show unmatched episodes
    if unmatched_count > 0:
        print(f"\n❌ Unmatched WURL Episodes:")
        for match in matches:
            if not match['matched']:
                wurl_ep = match['wurl_episode']
                print(f"  • Episode {wurl_ep['episode_number']}: {wurl_ep['title']} ({wurl_ep['video_filename']})")
    
    # Update database with WURL data
    if matched_count > 0:
        print(f"\n🔄 Updating database with WURL metadata...")
        updated_count = update_episodes_with_wurl_data(matches)
        print(f"✅ Updated {updated_count} episodes with WURL metadata")
    
    # Check GCS file existence
    gcs_results = check_gcs_files(wurl_episodes)
    found = [r for r in gcs_results if r[1]]
    missing = [r for r in gcs_results if not r[1]]
    print(f"\n📈 GCS File Check Results:")
    print(f"  ✅ Found: {len(found)}")
    print(f"  ❌ Missing: {len(missing)}")
    if missing:
        print("\n❌ Missing GCS files:")
        for ep, _, reason in missing:
            print(f"  • {ep['video_filename']} (Episode {ep['episode_number']}, {ep['title']}) - {reason}")
    print(f"\n🎉 Petrocelli WURL to GCS marriage complete!")

if __name__ == "__main__":
    main() 