#!/usr/bin/env python3
"""
Script to verify Man with a Camera episodes
"""

import psycopg2

def main():
    # Database connection
    conn = psycopg2.connect(
        host='localhost',
        database='pecantv',
        user='postgres',
        password='postgres',
        port='5433'
    )
    
    cursor = conn.cursor()
    
    print("📷 Verifying Man with a Camera episodes...")
    print("=" * 50)
    
    # Find Man with a Camera series
    cursor.execute("SELECT id, title FROM content WHERE title = 'Man With a Camera' AND type = 'SERIES'")
    series_info = cursor.fetchone()
    if not series_info:
        print("❌ Man With a Camera series not found!")
        return
    
    series_id, series_title = series_info
    print(f"✅ Found series: {series_title} (ID: {series_id})")
    
    # Check episodes
    cursor.execute("""
        SELECT id, title, season_number, episode_number, content_url, thumbnail_url
        FROM episodes 
        WHERE series_id = %s
        ORDER BY season_number, episode_number
    """, (series_id,))
    
    episodes = cursor.fetchall()
    print(f"\n📷 Man with a Camera episodes ({len(episodes)} total):")
    print("-" * 50)
    
    for row in episodes:
        ep_id, title, season, episode, content_url, thumbnail_url = row
        print(f"  S{season:02d}E{episode:02d} - {title}")
        print(f"    ID: {ep_id}")
        print(f"    Video: {content_url}")
        print(f"    Thumbnail: {thumbnail_url}")
        print()
    
    # Check if Eyewitness is correctly placed
    cursor.execute("""
        SELECT title, season_number, episode_number
        FROM episodes 
        WHERE series_id = %s AND title = 'Eyewitness'
    """, (series_id,))
    
    eyewitness = cursor.fetchone()
    if eyewitness:
        title, season, episode = eyewitness
        print(f"✅ 'Eyewitness' is correctly placed in Man with a Camera as S{season:02d}E{episode:02d}")
    else:
        print("❌ 'Eyewitness' not found in Man with a Camera series")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main() 