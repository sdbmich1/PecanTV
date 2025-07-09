#!/usr/bin/env python3
"""
Script to clean up duplicate content entries and fix Sherlock Holmes episodes.
"""

import psycopg2
import uuid

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def cleanup_duplicates():
    """Remove duplicate content entries."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # List of duplicate IDs to remove
    duplicate_ids = [658, 458, 629, 628, 548, 534, 627, 532, 522, 11, 12]
    
    print("Content to be deleted:")
    print("-" * 50)
    
    # Show what will be deleted
    for content_id in duplicate_ids:
        cur.execute("SELECT id, title, type FROM content WHERE id = %s", (content_id,))
        result = cur.fetchone()
        if result:
            print(f"ID {result[0]}: {result[1]} ({result[2]})")
        else:
            print(f"ID {content_id}: Not found")
    
    print("-" * 50)
    print(f"Total items to delete: {len(duplicate_ids)}")
    
    # Ask for confirmation
    response = input("\nDelete these duplicate entries? (y/n): ")
    if response.lower() == 'y':
        deleted_count = 0
        for content_id in duplicate_ids:
            try:
                cur.execute("DELETE FROM content WHERE id = %s", (content_id,))
                if cur.rowcount > 0:
                    deleted_count += 1
                    print(f"Deleted ID {content_id}")
                else:
                    print(f"ID {content_id} not found or already deleted")
            except Exception as e:
                print(f"Error deleting ID {content_id}: {e}")
        
        conn.commit()
        print(f"\nSuccessfully deleted {deleted_count} duplicate entries!")
    else:
        print("Deletion cancelled.")
    
    conn.close()

def fix_sherlock_holmes_episodes():
    """Fix Sherlock Holmes episodes to be properly linked to the series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Sherlock Holmes series ID (need to find it)
    cur.execute("SELECT id, uuid FROM content WHERE title LIKE '%Sherlock Holmes%' AND type = 'SERIES'")
    series_result = cur.fetchone()
    
    if not series_result:
        print("Sherlock Holmes series not found!")
        conn.close()
        return
    
    sherlock_series_id = series_result[0]
    series_uuid = series_result[1]
    print(f"Found Sherlock Holmes series with ID: {sherlock_series_id}")
    
    # Episodes to fix: 678, 679, 681
    episode_ids = [678, 679, 681]
    
    print("\nSherlock Holmes episodes to fix:")
    print("-" * 50)
    
    for episode_id in episode_ids:
        cur.execute("SELECT id, title, type FROM content WHERE id = %s", (episode_id,))
        result = cur.fetchone()
        if result:
            print(f"ID {result[0]}: {result[1]} ({result[2]})")
        else:
            print(f"ID {episode_id}: Not found")
    
    print("-" * 50)
    
    # Ask for confirmation
    response = input("\nFix these Sherlock Holmes episodes? (y/n): ")
    if response.lower() == 'y':
        # Fix each episode
        for i, episode_id in enumerate(episode_ids, 1):
            # Get episode UUID, title, and content_url
            cur.execute("SELECT uuid, title, content_url FROM content WHERE id = %s", (episode_id,))
            episode_result = cur.fetchone()
            if not episode_result:
                print(f"Episode {episode_id} not found!")
                continue
                
            episode_uuid = episode_result[0]
            episode_title = episode_result[1]
            episode_content_url = episode_result[2]
            
            # Check if episode already exists in episodes table
            cur.execute("SELECT id FROM episodes WHERE content_uuid = %s", (episode_uuid,))
            episode_exists = cur.fetchone()
            
            if episode_exists:
                print(f"Episode {episode_id} already exists in episodes table - updating series_id")
                cur.execute("""
                    UPDATE episodes 
                    SET series_id = %s, episode_number = %s
                    WHERE content_uuid = %s
                """, (sherlock_series_id, i, episode_uuid))
            else:
                print(f"Episode {episode_id} not in episodes table - adding it")
                # Add to episodes table with season_number=1, content_url, and uuid
                new_episode_uuid = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO episodes (series_id, season_number, episode_number, title, content_uuid, content_url, uuid)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (sherlock_series_id, 1, i, episode_title, episode_uuid, episode_content_url, new_episode_uuid))
            
            # Update content type to EPISODE
            cur.execute("UPDATE content SET type = 'EPISODE' WHERE id = %s", (episode_id,))
            print(f"Fixed episode {episode_id}")
        
        conn.commit()
        print("Successfully fixed Sherlock Holmes episodes!")
    else:
        print("Sherlock Holmes episode fix cancelled.")
    
    conn.close()

def show_final_state():
    """Show the final state after cleanup."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    print("\nFinal content count:")
    print("-" * 30)
    
    cur.execute("SELECT type, COUNT(*) FROM content GROUP BY type ORDER BY type")
    results = cur.fetchall()
    
    for content_type, count in results:
        print(f"{content_type}: {count}")
    
    total = sum(count for _, count in results)
    print(f"Total: {total}")
    
    conn.close()

def main():
    """Main cleanup function."""
    print("PecanTV Database Cleanup Script")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Remove duplicate content entries")
        print("2. Fix Sherlock Holmes episodes")
        print("3. Show final content count")
        print("4. Run all cleanup operations")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ")
        
        if choice == '1':
            cleanup_duplicates()
        elif choice == '2':
            fix_sherlock_holmes_episodes()
        elif choice == '3':
            show_final_state()
        elif choice == '4':
            print("\nRunning all cleanup operations...")
            cleanup_duplicates()
            fix_sherlock_holmes_episodes()
            show_final_state()
            print("\nAll cleanup operations completed!")
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please select 1-5.")

if __name__ == "__main__":
    main() 