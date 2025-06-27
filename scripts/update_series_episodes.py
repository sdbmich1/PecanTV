#!/usr/bin/env python3
"""
Script to update the database with proper episode relationships for classic series.
This script will:
1. Find all individual episode films for each series
2. Create proper episode records in the episodes table
3. Link episodes to their parent series
"""

import psycopg2
import uuid
from datetime import datetime, timezone
import re

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# Series definitions with their search patterns and metadata
SERIES_DEFINITIONS = {
    'Petrocelli': {
        'series_id': 21,
        'series_uuid': 'f3a8b22b-0eee-42bf-8c2f-d40be637cbcc',
        'search_pattern': 'Petrocelli',
        'episode_pattern': r'Petrocelli[-\s]+(.+)',
        'runtime': 44,
        'genre_id': 9,  # Drama
        'rating_id': 4,  # TVPG
        'poster_url': 'https://storage.googleapis.com/pecantv_title_images/Petrocelli_title-img.jpg'
    },
    'Dragnet': {
        'series_id': 68,
        'series_uuid': '5464912e-44e7-4e1b-a320-540048f17f54',
        'search_pattern': 'Dragnet Animated',
        'episode_pattern': r'Dragnet Animated[-\s]+Episode[-\s]+(\w+)',
        'runtime': 58,
        'genre_id': 7,  # Crime
        'rating_id': 2,  # TVY7
        'poster_url': 'https://storage.googleapis.com/pecantv_title_images/Dragnet_title-img.png'
    },
    'Lone Ranger': {
        'series_id': None,  # Need to find the main series
        'series_uuid': None,
        'search_pattern': 'Lone Ranger',
        'episode_pattern': r'Chapter[-\s]+(\d+)[-\s]+(.+)',
        'runtime': 22,
        'genre_id': 1,  # Action
        'rating_id': 2,  # TVY7
        'poster_url': 'https://storage.googleapis.com/pecantv_title_images/LoneRanger_TitleImage.png'
    },
    'Green Hornet': {
        'series_id': None,  # Need to find the main series
        'series_uuid': None,
        'search_pattern': 'Green Hornet',
        'episode_pattern': r'Chapter[-\s]+(\d+)[-\s]+(.+)',
        'runtime': 22,
        'genre_id': 12,  # Fantasy
        'rating_id': 2,  # TVY7
        'poster_url': 'https://storage.googleapis.com/pecantv_title_images/GreenHornet1Title3D-Lite.png'
    },
    'Commando Cody': {
        'series_id': 86,
        'series_uuid': '26b2f25d-d683-4a9c-8126-c017854edf9d',
        'search_pattern': 'Commando Cody',
        'episode_pattern': r'Chapter[-\s]+(\d+)[-\s]+(.+)',
        'runtime': 22,
        'genre_id': 12,  # Fantasy
        'rating_id': 2,  # TVY7
        'poster_url': 'https://storage.googleapis.com/pecantv_title_images/CommandoCodyTitleImg.jpg'
    },
    'Ghost Squad': {
        'series_id': 62,
        'series_uuid': 'd23243f8-eb8a-43ad-a067-a83fcf7583ae',
        'search_pattern': 'Ghost Squad',
        'episode_pattern': None,  # No episodes found yet
        'runtime': 50,
        'genre_id': 7,  # Crime
        'rating_id': 4,  # TVPG
        'poster_url': 'https://storage.googleapis.com/pecantv_title_images/Ghost-Squad_title-img.png'
    }
}

def get_series_info(conn, series_name):
    """Get the main series record for a given series name"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, uuid FROM content 
            WHERE title = %s AND type = 'SERIES'
        """, (series_name,))
        result = cur.fetchone()
        if result:
            return {'id': result[0], 'uuid': str(result[1])}
    return None

def find_episode_content(conn, search_pattern):
    """Find all content that matches the episode pattern for a series"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, uuid, title, description, content_url, poster_url, release_date
            FROM content 
            WHERE title ILIKE %s AND type = 'FILM'
            ORDER BY title
        """, (f'%{search_pattern}%',))
        return cur.fetchall()

def extract_episode_info(title, episode_pattern):
    """Extract episode number and title from content title"""
    if not episode_pattern:
        return None, title
    
    match = re.search(episode_pattern, title, re.IGNORECASE)
    if match:
        if len(match.groups()) == 1:
            # Pattern like "Episode One" or "Chapter 1"
            episode_num = match.group(1)
            # Convert text numbers to digits
            episode_num = convert_text_to_number(episode_num)
            return episode_num, title
        elif len(match.groups()) == 2:
            # Pattern like "Chapter 1 - Title"
            episode_num = convert_text_to_number(match.group(1))
            episode_title = match.group(2).strip()
            return episode_num, episode_title
    
    return None, title

def convert_text_to_number(text):
    """Convert text numbers (One, Two, etc.) to digits"""
    text = text.lower().strip()
    number_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15
    }
    
    if text in number_map:
        return number_map[text]
    
    # Try to convert directly to int
    try:
        return int(text)
    except ValueError:
        return None

def create_episode_record(conn, episode_data, series_info):
    """Create an episode record in the episodes table"""
    with conn.cursor() as cur:
        # Check if episode already exists
        cur.execute("""
            SELECT id FROM episodes 
            WHERE series_id = %s AND season_number = %s AND episode_number = %s
        """, (series_info['id'], 1, episode_data['episode_number']))
        
        if cur.fetchone():
            print(f"  Episode {episode_data['episode_number']} already exists, skipping...")
            return
        
        # Insert new episode
        cur.execute("""
            INSERT INTO episodes (
                uuid, title, description, season_number, episode_number, 
                runtime, content_url, poster_url, air_date, series_id, 
                content_uuid, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            str(uuid.uuid4()),
            episode_data['title'],
            episode_data['description'],
            1,  # season_number
            episode_data['episode_number'],
            episode_data['runtime'],
            episode_data['content_url'],
            episode_data['poster_url'],
            episode_data['release_date'],
            series_info['id'],
            series_info['uuid'],
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        print(f"  Created episode {episode_data['episode_number']}: {episode_data['title']}")

def process_series(conn, series_name, series_def):
    """Process a single series and create episode records"""
    print(f"\nProcessing {series_name}...")
    
    # Get series info if not provided
    if not series_def['series_id']:
        series_info = get_series_info(conn, series_name)
        if not series_info:
            print(f"  Could not find main series record for {series_name}")
            return
        series_def['series_id'] = series_info['id']
        series_def['series_uuid'] = series_info['uuid']
    
    # Find episode content
    episode_content = find_episode_content(conn, series_def['search_pattern'])
    
    if not episode_content:
        print(f"  No episode content found for {series_name}")
        return
    
    print(f"  Found {len(episode_content)} episode content items")
    
    # Process each episode
    for content_id, content_uuid, title, description, content_url, poster_url, release_date in episode_content:
        episode_num, episode_title = extract_episode_info(title, series_def['episode_pattern'])
        
        if episode_num is None:
            print(f"  Could not extract episode number from: {title}")
            continue
        
        episode_data = {
            'title': episode_title,
            'description': description,
            'episode_number': episode_num,
            'runtime': series_def['runtime'],
            'content_url': content_url or '',
            'poster_url': poster_url or series_def['poster_url'],
            'release_date': release_date
        }
        
        create_episode_record(conn, episode_data, {
            'id': series_def['series_id'],
            'uuid': series_def['series_uuid']
        })

def main():
    """Main function to update all series with episodes"""
    print("Starting series episode update...")
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Connected to database successfully")
        
        # Process each series
        for series_name, series_def in SERIES_DEFINITIONS.items():
            process_series(conn, series_name, series_def)
        
        conn.commit()
        print("\n✅ All series processed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 