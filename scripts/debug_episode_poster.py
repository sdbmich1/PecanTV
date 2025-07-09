#!/usr/bin/env python3
"""
Debug script to check episode poster URLs
"""

import psycopg2
import requests
import json

# Database connection
DB_CONFIG = {
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'sslmode': 'require'
}

def check_database():
    """Check what's in the database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check Bonanza episodes
        cursor.execute("""
            SELECT id, title, poster_url, thumbnail_url 
            FROM episodes 
            WHERE series_id = 78 
            LIMIT 3
        """)
        
        episodes = cursor.fetchall()
        print("Database episodes:")
        for episode in episodes:
            print(f"  ID: {episode[0]}, Title: {episode[1]}")
            print(f"    poster_url: {episode[2]}")
            print(f"    thumbnail_url: {episode[3]}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

def check_api():
    """Check what the API returns"""
    try:
        # Check API response
        response = requests.get("http://localhost:8000/series/78/episodes")
        if response.status_code == 200:
            episodes = response.json()
            print("API episodes:")
            for episode in episodes[:3]:
                print(f"  Title: {episode['title']}")
                print(f"    posterURL: {episode['posterURL']}")
                print()
        else:
            print(f"API error: {response.status_code}")
            
    except Exception as e:
        print(f"API error: {e}")

if __name__ == "__main__":
    print("=== Database Check ===")
    check_database()
    
    print("=== API Check ===")
    check_api() 