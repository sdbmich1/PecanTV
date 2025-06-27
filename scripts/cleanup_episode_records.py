#!/usr/bin/env python3
"""
Script to clean up content table records that are actually episodes.
"""

import psycopg2
import uuid
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

def analyze_potential_episodes():
    """Analyze content table for potential episode records."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Analyzing Content Table for Episode Records")
        print("=" * 55)
        
        # Get all potential episode records
        cur.execute('''
            SELECT id, title, type, description, runtime, content_url, poster_url
            FROM content 
            WHERE (type = 'FILM' OR type = 'SERIES') 
            AND (
                title LIKE '%Episode%' 
                OR title LIKE '%S%' AND title LIKE '%E%'
                OR title LIKE '% - %'
                OR title LIKE '% Part %'
                OR title LIKE '% Chapter %'
                OR title LIKE '% Season %'
            )
            ORDER BY type, title
        ''')
        
        records = cur.fetchall()
        
        if not records:
            print("✅ No potential episode records found")
            return []
        
        print(f"📋 Found {len(records)} potential episode records:")
        print()
        
        # Group by patterns
        chapter_records = []
        part_records = []
        other_records = []
        
        for record in records:
            title = record[1]
            if 'Chapter' in title:
                chapter_records.append(record)
            elif 'Part' in title:
                part_records.append(record)
            else:
                other_records.append(record)
        
        if chapter_records:
            print(f"📖 Chapter records ({len(chapter_records)}):")
            for record in chapter_records[:5]:
                print(f"  • {record[1]} ({record[2]}, ID: {record[0]})")
            if len(chapter_records) > 5:
                print(f"  ... and {len(chapter_records) - 5} more")
            print()
        
        if part_records:
            print(f"📝 Part records ({len(part_records)}):")
            for record in part_records:
                print(f"  • {record[1]} ({record[2]}, ID: {record[0]})")
            print()
        
        if other_records:
            print(f"🔍 Other potential episodes ({len(other_records)}):")
            for record in other_records:
                print(f"  • {record[1]} ({record[2]}, ID: {record[0]})")
            print()
        
        return records
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def cleanup_episode_records(records):
    """Clean up episode records from content table."""
    if not records:
        print("No records to clean up")
        return
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🧹 Cleaning Up Episode Records")
        print("=" * 40)
        
        deleted_count = 0
        kept_count = 0
        
        # Define legitimate films that should be kept
        legitimate_films = [
            'Jesse Owens: The Fastest Man in the World Part I',
            'Jesse Owens: The Fastest Man in the World Part II',
            'Sherlock Holmes - Terror By Night',
            'Dick Tracy vs Cueball',
            'Dick Tracy Meets Gruesome'
        ]
        
        for record in records:
            content_id, title, content_type, description, runtime, content_url, poster_url = record
            
            # Check if this is a legitimate film that should be kept
            should_keep = False
            for legitimate_film in legitimate_films:
                if legitimate_film.lower() in title.lower():
                    should_keep = True
                    break
            
            if should_keep:
                print(f"  ✅ Keeping legitimate film: {title} (ID: {content_id})")
                kept_count += 1
            else:
                # This is an episode record that should be deleted
                cur.execute("DELETE FROM content WHERE id = %s", (content_id,))
                print(f"  🗑️  Deleted episode: {title} (ID: {content_id})")
                deleted_count += 1
        
        conn.commit()
        print(f"\n📊 Cleanup Summary:")
        print(f"  • Deleted: {deleted_count} episode records")
        print(f"  • Kept: {kept_count} legitimate films")
        
        # Show final content table counts
        cur.execute("SELECT type, COUNT(*) FROM content GROUP BY type ORDER BY COUNT(*) DESC")
        type_counts = cur.fetchall()
        print(f"\n📋 Final Content Table Distribution:")
        for content_type, count in type_counts:
            print(f"  • {content_type}: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to analyze and clean up episode records."""
    print("🎬 Content Table Episode Cleanup")
    print("=" * 40)
    
    # Analyze potential episodes
    records = analyze_potential_episodes()
    
    if not records:
        return
    
    # Ask for confirmation
    response = input(f"\nDo you want to clean up {len(records)} potential episode records? (y/n): ").lower().strip()
    
    if response == 'y':
        cleanup_episode_records(records)
        print("\n✅ Cleanup completed!")
    else:
        print("❌ Cleanup cancelled")

if __name__ == "__main__":
    main() 