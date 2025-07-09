#!/usr/bin/env python3
"""
Database backup script to preserve current episode state before restoration.
This creates a backup of all current episodes and series relationships.
"""

import psycopg2
import json
import os
from datetime import datetime

# Database connection parameters for local database
DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

def backup_episodes():
    """Create a complete backup of current episodes and series data."""
    
    print("🔒 Creating Database Backup")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Get current timestamp for backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"episode_backup_{timestamp}.json"
        
        backup_data = {
            "backup_timestamp": timestamp,
            "backup_description": "Episode and series backup before restoration",
            "series": [],
            "episodes": [],
            "content": []
        }
        
        # Backup series data
        print("📺 Backing up series data...")
        cursor.execute("""
            SELECT id, title, type, poster_url, description, runtime, created_at, updated_at
            FROM content 
            WHERE type = 'SERIES'
            ORDER BY title
        """)
        
        series_data = cursor.fetchall()
        for series in series_data:
            backup_data["series"].append({
                "id": series[0],
                "title": series[1],
                "type": series[2],
                "poster_url": series[3],
                "description": series[4],
                "runtime": series[5],
                "created_at": str(series[6]) if series[6] else None,
                "updated_at": str(series[7]) if series[7] else None
            })
        
        print(f"  ✅ Backed up {len(series_data)} series")
        
        # Backup episodes data
        print("🎬 Backing up episodes data...")
        cursor.execute("""
            SELECT id, series_id, season_number, episode_number, title, description,
                   content_url, thumbnail_url, runtime, air_date, created_at, updated_at
            FROM episodes 
            ORDER BY series_id, season_number, episode_number
        """)
        
        episodes_data = cursor.fetchall()
        for episode in episodes_data:
            backup_data["episodes"].append({
                "id": episode[0],
                "series_id": episode[1],
                "season_number": episode[2],
                "episode_number": episode[3],
                "title": episode[4],
                "description": episode[5],
                "content_url": episode[6],
                "thumbnail_url": episode[7],
                "runtime": episode[8],
                "air_date": str(episode[9]) if episode[9] else None,
                "created_at": str(episode[10]) if episode[10] else None,
                "updated_at": str(episode[11]) if episode[11] else None
            })
        
        print(f"  ✅ Backed up {len(episodes_data)} episodes")
        
        # Backup content data (films and other content)
        print("🎭 Backing up content data...")
        cursor.execute("""
            SELECT id, title, type, poster_url, trailer_url, content_url, description,
                   runtime, genre_id, rating_id, release_date, created_at, updated_at, uuid
            FROM content 
            WHERE type = 'FILM'
            ORDER BY title
        """)
        
        content_data = cursor.fetchall()
        for content in content_data:
            backup_data["content"].append({
                "id": content[0],
                "title": content[1],
                "type": content[2],
                "poster_url": content[3],
                "trailer_url": content[4],
                "content_url": content[5],
                "description": content[6],
                "runtime": content[7],
                "genre_id": content[8],
                "rating_id": content[9],
                "release_date": str(content[10]) if content[10] else None,
                "created_at": str(content[11]) if content[11] else None,
                "updated_at": str(content[12]) if content[12] else None,
                "uuid": str(content[13]) if content[13] else None
            })
        
        print(f"  ✅ Backed up {len(content_data)} content items")
        
        # Save backup to file
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"\n💾 Backup saved to: {backup_file}")
        
        # Create summary
        print(f"\n📊 Backup Summary:")
        print(f"  • Series: {len(series_data)}")
        print(f"  • Episodes: {len(episodes_data)}")
        print(f"  • Content: {len(content_data)}")
        print(f"  • Total records: {len(series_data) + len(episodes_data) + len(content_data)}")
        
        # Show episode counts by series
        print(f"\n🎬 Current Episode Counts by Series:")
        cursor.execute("""
            SELECT c.title, COUNT(e.id) as episode_count
            FROM content c
            LEFT JOIN episodes e ON c.id = e.series_id
            WHERE c.type = 'SERIES'
            GROUP BY c.id, c.title
            ORDER BY episode_count DESC, c.title
        """)
        
        episode_counts = cursor.fetchall()
        for title, count in episode_counts:
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {title}: {count} episodes")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Backup completed successfully!")
        print(f"📁 Backup file: {backup_file}")
        print(f"🔄 To restore: Use restore_from_backup.py with this file")
        
        return backup_file
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def create_restore_script(backup_file):
    """Create a restore script for the backup."""
    
    restore_script = f'''#!/usr/bin/env python3
"""
Restore script for backup: {backup_file}
Run this script to restore the database to the state when this backup was created.
"""

import psycopg2
import json
import sys

# Database connection parameters
DB_PARAMS = {{
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}}

def restore_from_backup(backup_file):
    """Restore database from backup file."""
    
    print(f"🔄 Restoring from backup: {{backup_file}}")
    
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
        print(f"❌ Restore failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    restore_from_backup("{backup_file}")
'''
    
    restore_filename = f"restore_from_backup_{backup_file.replace('episode_backup_', '').replace('.json', '')}.py"
    with open(restore_filename, 'w') as f:
        f.write(restore_script)
    
    print(f"📝 Restore script created: {restore_filename}")
    return restore_filename

if __name__ == "__main__":
    backup_file = backup_episodes()
    if backup_file:
        restore_script = create_restore_script(backup_file)
        print(f"\n🎯 Next steps:")
        print(f"1. Review the backup: {backup_file}")
        print(f"2. Keep the restore script: {restore_script}")
        print(f"3. Proceed with episode restoration")
        print(f"4. If issues occur, run: python3 {restore_script}") 