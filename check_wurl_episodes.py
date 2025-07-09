#!/usr/bin/env python3
import csv
import psycopg2
import os

def check_wurl_episodes():
    """Check what episodes are in the Wurl metadata files"""
    
    # Check the latest Wurl CSV file
    csv_file = "Wurl - File Upload Metadata_Version 7.0.64.csv"
    
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found")
        return
    
    series_episodes = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                series_name = row.get('Series Name', '').strip()
                title = row.get('Title', '').strip()
                episode_number = row.get('Episode Number', '').strip()
                season_number = row.get('Season Number', '').strip()
                entry_type = row.get('Entry Type', '').strip()
                
                if series_name and entry_type == 'Episode':
                    if series_name not in series_episodes:
                        series_episodes[series_name] = []
                    
                    series_episodes[series_name].append({
                        'title': title,
                        'season': season_number,
                        'episode': episode_number
                    })
    
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    print("Episodes found in Wurl metadata:")
    for series, episodes in sorted(series_episodes.items()):
        print(f"\n{series}: {len(episodes)} episodes")
        for ep in episodes[:5]:  # Show first 5 episodes
            print(f"  S{ep['season']}E{ep['episode']}: {ep['title']}")
        if len(episodes) > 5:
            print(f"  ... and {len(episodes) - 5} more")

def check_database_episodes():
    """Check what episodes are currently in the database"""
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='pecantv',
            user='postgres',
            password='postgres'
        )
        cursor = conn.cursor()
        
        # Get series with episode counts
        cursor.execute("""
            SELECT c.id, c.title, COUNT(e.id) as episode_count
            FROM content c
            LEFT JOIN episodes e ON c.id = e.series_id
            WHERE c.type = 'SERIES'
            GROUP BY c.id, c.title
            ORDER BY c.title
        """)
        
        series_data = cursor.fetchall()
        
        print("\nEpisodes currently in database:")
        for series_id, title, count in series_data:
            print(f"  {series_id}: {title} - {count} episodes")
            
            # Show episode details for series with episodes
            if count > 0:
                cursor.execute("""
                    SELECT season_number, episode_number, title
                    FROM episodes 
                    WHERE series_id = %s 
                    ORDER BY season_number, episode_number
                """, (series_id,))
                
                episodes = cursor.fetchall()
                for season, episode, ep_title in episodes:
                    print(f"    S{season}E{episode}: {ep_title}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    check_wurl_episodes()
    check_database_episodes() 