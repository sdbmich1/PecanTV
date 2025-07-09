#!/usr/bin/env python3
"""
Script to remove episodes from the database that don't have corresponding GCS files
"""

import os
import sys
import requests
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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
        if "pooler" in parsed.netloc:
            # Already using pooler
            return database_url
        else:
            # Convert to pooler URL
            pooler_url = database_url.replace("neon.tech", "neon.tech/pooler")
            return pooler_url
    
    return database_url

def check_gcs_file_exists(content_url):
    """
    Check if a GCS file exists by making a HEAD request
    """
    try:
        response = requests.head(content_url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Error checking {content_url}: {e}")
        return False

def main():
    print("🔍 Checking for episodes with missing GCS files...")
    
    # Connect to database
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all episodes with their content URLs
        query = text("""
            SELECT id, episode_number, title, content_url, series_id 
            FROM episodes 
            WHERE content_url IS NOT NULL AND content_url != ''
            ORDER BY series_id, episode_number
        """)
        
        result = session.execute(query)
        episodes = result.fetchall()
        
        print(f"📊 Found {len(episodes)} episodes to check")
        
        missing_files = []
        existing_files = []
        
        for episode in episodes:
            episode_id, episode_number, title, content_url, series_id = episode
            
            print(f"🔍 Checking episode {episode_number}: {title}")
            
            if check_gcs_file_exists(content_url):
                existing_files.append(episode)
                print(f"  ✅ File exists: {content_url}")
            else:
                missing_files.append(episode)
                print(f"  ❌ File missing: {content_url}")
        
        print(f"\n📈 Summary:")
        print(f"  ✅ Episodes with existing files: {len(existing_files)}")
        print(f"  ❌ Episodes with missing files: {len(missing_files)}")
        
        if missing_files:
            print(f"\n🗑️  Episodes to be removed (missing GCS files):")
            for episode in missing_files:
                episode_id, episode_number, title, content_url, series_id = episode
                print(f"  - Episode {episode_number}: {title} (ID: {episode_id})")
                print(f"    Missing: {content_url}")
            
            # Ask for confirmation
            response = input(f"\n❓ Do you want to remove {len(missing_files)} episodes with missing GCS files? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                print("🗑️  Removing episodes with missing GCS files...")
                
                for episode in missing_files:
                    episode_id, episode_number, title, content_url, series_id = episode
                    
                    # Delete the episode
                    delete_query = text("DELETE FROM episodes WHERE id = :episode_id")
                    session.execute(delete_query, {"episode_id": episode_id})
                    
                    print(f"  ✅ Removed episode {episode_number}: {title}")
                
                # Commit the changes
                session.commit()
                print(f"\n✅ Successfully removed {len(missing_files)} episodes with missing GCS files")
            else:
                print("❌ Operation cancelled")
        else:
            print("🎉 All episodes have corresponding GCS files!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main() 