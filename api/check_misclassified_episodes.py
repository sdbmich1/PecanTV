#!/usr/bin/env python3
"""
Script to check for misclassified episodes
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
    
    print("🔍 Checking for misclassified episodes...")
    print("=" * 50)
    
    # Check for "My Fair Deadly" in content table
    print("\n🎬 Looking for 'My Fair Deadly'...")
    cursor.execute("""
        SELECT id, title, type, poster_url, description
        FROM content 
        WHERE title ILIKE '%my fair deadly%'
        ORDER BY id
    """)
    
    my_fair_deadly_results = cursor.fetchall()
    print(f"Found {len(my_fair_deadly_results)} entries for 'My Fair Deadly':")
    for row in my_fair_deadly_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
        print(f"  Poster: {row[3]}")
        print(f"  Description: {row[4][:100]}..." if row[4] else "  Description: None")
        print()
    
    # Check for "Eyewitness" in content table
    print("\n👁️ Looking for 'Eyewitness'...")
    cursor.execute("""
        SELECT id, title, type, poster_url, description
        FROM content 
        WHERE title ILIKE '%eyewitness%'
        ORDER BY id
    """)
    
    eyewitness_results = cursor.fetchall()
    print(f"Found {len(eyewitness_results)} entries for 'Eyewitness':")
    for row in eyewitness_results:
        print(f"  ID: {row[0]}, Title: '{row[1]}', Type: {row[2]}")
        print(f"  Poster: {row[3]}")
        print(f"  Description: {row[4][:100]}..." if row[4] else "  Description: None")
        print()
    
    # Check Mike Hammer episodes
    print("\n🔍 Checking Mike Hammer episodes...")
    cursor.execute("""
        SELECT id, title, season_number, episode_number
        FROM episodes 
        WHERE series_id = (SELECT id FROM content WHERE title = 'Mike Hammer' AND type = 'SERIES')
        ORDER BY season_number, episode_number
    """)
    
    mh_episodes = cursor.fetchall()
    print(f"Found {len(mh_episodes)} Mike Hammer episodes:")
    for row in mh_episodes:
        print(f"  S{row[2]:02d}E{row[3]:02d} - {row[1]}")
    
    # Check Married with Children episodes
    print("\n👨‍👩‍👧‍👦 Checking Married with Children episodes...")
    cursor.execute("""
        SELECT id, title, season_number, episode_number
        FROM episodes 
        WHERE series_id = (SELECT id FROM content WHERE title = 'Married with Children' AND type = 'SERIES')
        ORDER BY season_number, episode_number
    """)
    
    mwc_episodes = cursor.fetchall()
    print(f"Found {len(mwc_episodes)} Married with Children episodes:")
    for row in mwc_episodes:
        print(f"  S{row[2]:02d}E{row[3]:02d} - {row[1]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main() 