#!/usr/bin/env python3
"""
Restore script for backup: episode_backup_20250705_201738.json
Run this script to restore the database to the state when this backup was created.
"""

import psycopg2
import json
import sys

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def restore_from_backup(backup_file):
    """Restore database from backup file."""
    
    print(f"🔄 Restoring from backup: {backup_file}")
    
    try:
        # Load backup data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Clear current data
        print("🧹 Clearing current episodes...")
        cursor.execute("DELETE FROM episodes")
        
        print("🧹 Clearing current content...")
        cursor.execute("DELETE FROM content WHERE type IN ('SERIES', 'FILM')")
        
        # Restore content (series and films)
        print("📺 Restoring content...")
        for content in backup_data["content"] + backup_data["series"]:
            cursor.execute("""
                INSERT INTO content (
                    id, title, type, poster_url, trailer_url, content_url, description,
                    runtime, genre_id, rating_id, release_date, created_at, updated_at, uuid
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                content["id"], content["title"], content["type"], content["poster_url"],
                content.get("trailer_url"), content.get("content_url"), content["description"],
                content["runtime"], content.get("genre_id"), content.get("rating_id"),
                content.get("release_date"), content["created_at"], content["updated_at"],
                content.get("uuid")
            ))
        
        # Restore episodes
        print("🎬 Restoring episodes...")
        for episode in backup_data["episodes"]:
            cursor.execute("""
                INSERT INTO episodes (
                    id, series_id, season_number, episode_number, title, description,
                    content_url, thumbnail_url, runtime, air_date, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                episode["id"], episode["series_id"], episode["season_number"],
                episode["episode_number"], episode["title"], episode["description"],
                episode["content_url"], episode["thumbnail_url"], episode["runtime"],
                episode["air_date"], episode["created_at"], episode["updated_at"]
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Restore completed successfully!")
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    restore_from_backup("episode_backup_20250705_201738.json")
