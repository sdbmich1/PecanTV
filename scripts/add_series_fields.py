#!/usr/bin/env python3
"""
Script to add series_name and episode_number fields to the content table
and populate them based on the existing data structure.
"""

import psycopg2
import re
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

def add_series_fields():
    """Add series_name and episode_number columns to the content table."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Add series_name column
        print("Adding series_name column...")
        cur.execute("""
            ALTER TABLE content 
            ADD COLUMN IF NOT EXISTS series_name VARCHAR(255)
        """)
        
        # Add episode_number column
        print("Adding episode_number column...")
        cur.execute("""
            ALTER TABLE content 
            ADD COLUMN IF NOT EXISTS episode_number INTEGER
        """)
        
        # Add season_number column
        print("Adding season_number column...")
        cur.execute("""
            ALTER TABLE content 
            ADD COLUMN IF NOT EXISTS season_number INTEGER
        """)
        
        conn.commit()
        print("✅ Series fields added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding fields: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def extract_series_info(title, description):
    """Extract series name and episode number from title and description."""
    series_name = None
    episode_number = None
    season_number = 1  # Default to season 1
    
    # Common series patterns
    series_patterns = [
        r'Lone Ranger',
        r'Green Hornet', 
        r'Dragnet',
        r'Petrocelli',
        r'Commando Cody',
        r'Ghost Squad',
        r'Man with a Camera',
        r'Count Duckula',
        r'Count of Monte Cristo',
        r'Zorro',
        r'Longstreet'
    ]
    
    # Episode number patterns
    episode_patterns = [
        r'Chapter (\d+)',
        r'Episode (\d+)',
        r'Part (\d+)',
        r'(\d+)\s*[-–]\s*',  # Number followed by dash
    ]
    
    # Find series name
    for pattern in series_patterns:
        if re.search(pattern, title, re.IGNORECASE) or re.search(pattern, description or '', re.IGNORECASE):
            series_name = pattern
            break
    
    # Find episode number
    for pattern in episode_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            episode_number = int(match.group(1))
            break
    
    return series_name, episode_number, season_number

def populate_series_fields():
    """Populate series_name and episode_number fields based on existing data."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get all content
        cur.execute("SELECT id, title, description, type FROM content ORDER BY id")
        content_items = cur.fetchall()
        
        updated_count = 0
        
        for item_id, title, description, content_type in content_items:
            series_name, episode_number, season_number = extract_series_info(title, description)
            
            if series_name or episode_number:
                cur.execute("""
                    UPDATE content 
                    SET series_name = %s, episode_number = %s, season_number = %s
                    WHERE id = %s
                """, (series_name, episode_number, season_number, item_id))
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count} items...")
        
        conn.commit()
        print(f"✅ Updated {updated_count} content items with series information!")
        
    except Exception as e:
        print(f"❌ Error populating fields: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def verify_series_data():
    """Verify the series data was populated correctly."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Check series with episodes
        cur.execute("""
            SELECT series_name, COUNT(*) as episode_count, 
                   MIN(episode_number) as min_episode, 
                   MAX(episode_number) as max_episode
            FROM content 
            WHERE series_name IS NOT NULL 
            GROUP BY series_name 
            ORDER BY series_name
        """)
        
        series_data = cur.fetchall()
        
        print("\n📊 Series Data Summary:")
        print("-" * 60)
        for series_name, episode_count, min_ep, max_ep in series_data:
            print(f"{series_name}: {episode_count} episodes (Episodes {min_ep}-{max_ep})")
        
        # Show some sample episodes
        print("\n📺 Sample Episodes:")
        print("-" * 60)
        cur.execute("""
            SELECT title, series_name, episode_number, season_number 
            FROM content 
            WHERE series_name IS NOT NULL 
            ORDER BY series_name, episode_number 
            LIMIT 15
        """)
        
        episodes = cur.fetchall()
        for title, series, ep_num, season in episodes:
            print(f"{series} S{season}E{ep_num}: {title}")
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
    finally:
        cur.close()
        conn.close()

def main():
    print("🎬 Adding Series Fields to Content Table")
    print("=" * 50)
    
    # Step 1: Add the new columns
    add_series_fields()
    
    # Step 2: Populate the fields
    populate_series_fields()
    
    # Step 3: Verify the data
    verify_series_data()
    
    print("\n✅ Series fields setup complete!")

if __name__ == "__main__":
    main() 