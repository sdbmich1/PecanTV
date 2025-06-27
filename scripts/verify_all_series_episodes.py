#!/usr/bin/env python3
"""
Script to verify all series have episodes loaded from Wurl metadata files with proper content URLs and poster URLs.
"""

import psycopg2
import pandas as pd
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

def get_all_series_from_database():
    """Get all series from the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, title, type FROM content 
            WHERE type = 'SERIES'
            ORDER BY title
        """)
        
        series = cur.fetchall()
        return series
        
    except Exception as e:
        print(f"❌ Error getting series from database: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_episode_counts_for_series(series_id):
    """Get episode counts for a specific series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN content_url IS NULL OR content_url = '' THEN 1 END) as missing_content,
                COUNT(CASE WHEN content_url IS NOT NULL AND content_url != '' THEN 1 END) as has_content,
                COUNT(CASE WHEN poster_url IS NULL OR poster_url = '' THEN 1 END) as missing_poster,
                COUNT(CASE WHEN poster_url IS NOT NULL AND poster_url != '' THEN 1 END) as has_poster
            FROM episodes 
            WHERE series_id = %s
        """, (series_id,))
        
        result = cur.fetchone()
        if result:
            return {
                'total': result[0],
                'missing_content': result[1],
                'has_content': result[2],
                'missing_poster': result[3],
                'has_poster': result[4]
            }
        return None
        
    except Exception as e:
        print(f"❌ Error getting episode counts: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def find_series_in_wurl_files():
    """Find all series mentioned in Wurl metadata files."""
    print("🔍 Scanning Wurl metadata files for series...")
    
    # Find all Wurl metadata files with different patterns
    excel_files = glob.glob("Wurl*.xlsx") + glob.glob("Wurl - *.xlsx") + glob.glob("Wurl-File-Upload-Metadata*.xlsx")
    csv_files = glob.glob("Wurl*.csv") + glob.glob("Wurl - *.csv") + glob.glob("Wurl-File-Upload-Metadata*.csv")
    
    series_in_wurl = {}
    
    for file in excel_files + csv_files:
        try:
            if file.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                # Try different encodings for CSV
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    continue
            
            # Check for series data
            if 'Series Name' in df.columns:
                df['Series Name'] = df['Series Name'].astype(str).fillna('')
                
                for series_name in df['Series Name'].unique():
                    if series_name and series_name.strip() and series_name.strip().lower() != 'nan':
                        series_name_clean = series_name.strip()
                        if series_name_clean not in series_in_wurl:
                            series_in_wurl[series_name_clean] = {
                                'files': [],
                                'episode_count': 0,
                                'has_video_filenames': 0,
                                'has_artwork_filenames': 0
                            }
                        
                        if file not in series_in_wurl[series_name_clean]['files']:
                            series_in_wurl[series_name_clean]['files'].append(file)
                        
                        # Count episodes for this series
                        series_df = df[df['Series Name'].str.strip() == series_name_clean]
                        series_in_wurl[series_name_clean]['episode_count'] += len(series_df)
                        
                        # Count episodes with video filenames
                        if 'Video Filename' in df.columns:
                            video_count = len(series_df[series_df['Video Filename'].notna() & (series_df['Video Filename'] != '')])
                            series_in_wurl[series_name_clean]['has_video_filenames'] += video_count
                        
                        # Count episodes with artwork filenames
                        if 'Artwork Filename' in df.columns:
                            artwork_count = len(series_df[series_df['Artwork Filename'].notna() & (series_df['Artwork Filename'] != '')])
                            series_in_wurl[series_name_clean]['has_artwork_filenames'] += artwork_count
        
        except Exception as e:
            print(f"  ⚠️  Error reading {file}: {e}")
    
    return series_in_wurl

def verify_all_series():
    """Verify all series have episodes loaded from Wurl metadata files."""
    print("🎬 Verifying All Series Episodes from Wurl Metadata Files")
    print("=" * 70)
    
    # Get all series from database
    db_series = get_all_series_from_database()
    print(f"📊 Found {len(db_series)} series in database")
    
    # Get series from Wurl files
    wurl_series = find_series_in_wurl_files()
    print(f"📊 Found {len(wurl_series)} series in Wurl metadata files")
    
    print("\n📋 Series Analysis:")
    print("-" * 70)
    
    total_episodes_in_db = 0
    total_episodes_with_content = 0
    total_episodes_missing_content = 0
    total_episodes_with_poster = 0
    total_episodes_missing_poster = 0
    
    for series_id, series_title, series_type in db_series:
        print(f"\n🎬 {series_title} (ID: {series_id})")
        print("  " + "-" * 50)
        
        # Get episode counts from database
        episode_counts = get_episode_counts_for_series(series_id)
        if episode_counts:
            total_episodes_in_db += episode_counts['total']
            total_episodes_with_content += episode_counts['has_content']
            total_episodes_missing_content += episode_counts['missing_content']
            total_episodes_with_poster += episode_counts['has_poster']
            total_episodes_missing_poster += episode_counts['missing_poster']
            
            print(f"  📺 Database episodes: {episode_counts['total']}")
            print(f"     ✅ With content URLs: {episode_counts['has_content']}")
            print(f"     ❌ Missing content URLs: {episode_counts['missing_content']}")
            print(f"     ✅ With poster URLs: {episode_counts['has_poster']}")
            print(f"     ❌ Missing poster URLs: {episode_counts['missing_poster']}")
        
        # Check if series exists in Wurl files
        if series_title in wurl_series:
            wurl_info = wurl_series[series_title]
            print(f"  📁 Wurl metadata: {wurl_info['episode_count']} episodes in {len(wurl_info['files'])} files")
            print(f"     🎥 Episodes with video filenames: {wurl_info['has_video_filenames']}")
            print(f"     🖼️  Episodes with artwork filenames: {wurl_info['has_artwork_filenames']}")
            
            # Check if we need to load episodes
            if episode_counts and episode_counts['has_content'] == 0 and wurl_info['has_video_filenames'] > 0:
                print(f"     ⚠️  NEEDS LOADING: {wurl_info['has_video_filenames']} episodes available in Wurl files")
            elif episode_counts and episode_counts['has_content'] > 0:
                print(f"     ✅ LOADED: {episode_counts['has_content']} episodes have content URLs")
            else:
                print(f"     ❌ NO CONTENT: No episodes with content URLs found")
            
            # Check poster URLs
            if episode_counts and episode_counts['has_poster'] == 0 and wurl_info['has_artwork_filenames'] > 0:
                print(f"     ⚠️  NEEDS POSTERS: {wurl_info['has_artwork_filenames']} episodes have artwork filenames available")
            elif episode_counts and episode_counts['has_poster'] > 0:
                print(f"     ✅ POSTERS LOADED: {episode_counts['has_poster']} episodes have poster URLs")
            else:
                print(f"     ❌ NO POSTERS: No episodes with poster URLs found")
        else:
            print(f"  ❌ Not found in Wurl metadata files")
    
    # Summary
    print(f"\n📊 OVERALL SUMMARY:")
    print("=" * 70)
    print(f"  Total series in database: {len(db_series)}")
    print(f"  Total series in Wurl files: {len(wurl_series)}")
    print(f"  Total episodes in database: {total_episodes_in_db}")
    print(f"  Episodes with content URLs: {total_episodes_with_content}")
    print(f"  Episodes missing content URLs: {total_episodes_missing_content}")
    print(f"  Episodes with poster URLs: {total_episodes_with_poster}")
    print(f"  Episodes missing poster URLs: {total_episodes_missing_poster}")
    
    if total_episodes_missing_content > 0:
        print(f"\n⚠️  {total_episodes_missing_content} episodes still missing content URLs")
        print("   Consider running loading scripts for series with missing content URLs")
    else:
        print(f"\n✅ All episodes have content URLs!")
    
    if total_episodes_missing_poster > 0:
        print(f"\n⚠️  {total_episodes_missing_poster} episodes still missing poster URLs")
        print("   Consider running loading scripts for series with missing poster URLs")
    else:
        print(f"\n✅ All episodes have poster URLs!")
    
    # Show series that need loading
    print(f"\n🔧 SERIES THAT MAY NEED LOADING:")
    print("-" * 50)
    needs_loading = []
    
    for series_id, series_title, series_type in db_series:
        episode_counts = get_episode_counts_for_series(series_id)
        if episode_counts:
            needs_content = episode_counts['has_content'] == 0
            needs_poster = episode_counts['has_poster'] == 0
            
            if series_title in wurl_series:
                wurl_info = wurl_series[series_title]
                has_video = wurl_info['has_video_filenames'] > 0
                has_artwork = wurl_info['has_artwork_filenames'] > 0
                
                if needs_content and has_video or needs_poster and has_artwork:
                    needs_loading.append({
                        'title': series_title,
                        'id': series_id,
                        'wurl_episodes': wurl_info['has_video_filenames'],
                        'wurl_artwork': wurl_info['has_artwork_filenames'],
                        'needs_content': needs_content and has_video,
                        'needs_poster': needs_poster and has_artwork,
                        'files': wurl_info['files']
                    })
    
    if needs_loading:
        for series in needs_loading:
            print(f"  📺 {series['title']} (ID: {series['id']})")
            if series['needs_content']:
                print(f"     🎥 Needs content URLs: {series['wurl_episodes']} episodes available")
            if series['needs_poster']:
                print(f"     🖼️  Needs poster URLs: {series['wurl_artwork']} episodes available")
            print(f"     Files: {', '.join([f.split('_')[1] for f in series['files'][:3]])}...")
    else:
        print("  ✅ All series appear to have episodes loaded with content and poster URLs!")

if __name__ == "__main__":
    verify_all_series() 