#!/usr/bin/env python3
"""
Script to adjust episode counts to match actual content.
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

# Target episode counts (to be adjusted based on actual content)
TARGET_EPISODE_COUNTS = {
    'Bonanza': 13,  # Reduce from 29 to 13
    'Count of Monte Cristo': 39,  # Keep as is for now
    'Petrocelli': 21,  # Keep as is for now
    'Longstreet': 20,  # Keep as is for now
    'Lone Ranger': 14,  # Keep as is for now
    'Commando Cody': 12,  # Keep as is for now
    'Dragnet': 10,  # Keep as is for now
    'Ghost Squad': 4,  # Keep as is for now
    'Mike Hammer': 4,  # Keep as is for now
    'Man with a Camera': 3,  # Keep as is for now
}

def get_current_episode_counts():
    """Get current episode counts for all series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        cur.execute('''
            SELECT c.title, COUNT(e.id) as episode_count
            FROM content c
            LEFT JOIN episodes e ON e.series_id = c.id
            WHERE c.type = 'SERIES'
            GROUP BY c.id, c.title
            ORDER BY episode_count DESC, c.title
        ''')
        
        results = cur.fetchall()
        return {title: count for title, count in results if count > 0}
        
    finally:
        cur.close()
        conn.close()

def adjust_episode_count(series_name, target_count):
    """Adjust episode count for a specific series."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print(f"\n🎬 Adjusting {series_name} episodes")
        print("=" * 40)
        
        # Get series ID
        cur.execute('SELECT id FROM content WHERE type = %s AND title = %s', ('SERIES', series_name))
        series_id = cur.fetchone()[0]
        
        # Get current episodes
        cur.execute('''
            SELECT id, title, season_number, episode_number
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY season_number, episode_number
        ''', (series_id,))
        
        episodes = cur.fetchall()
        current_count = len(episodes)
        
        print(f"Current episodes: {current_count}")
        print(f"Target episodes: {target_count}")
        
        if current_count == target_count:
            print("✅ Episode count already matches target")
            return
        
        if current_count > target_count:
            # Remove excess episodes (keep first N)
            episodes_to_remove = episodes[target_count:]
            episode_ids_to_remove = [ep[0] for ep in episodes_to_remove]
            
            print(f"Removing {len(episodes_to_remove)} excess episodes:")
            for ep in episodes_to_remove:
                print(f"  • S{ep[2]}E{ep[3]}: {ep[1]}")
            
            cur.execute('DELETE FROM episodes WHERE id = ANY(%s)', (episode_ids_to_remove,))
            print(f"✅ Removed {len(episodes_to_remove)} episodes")
            
        else:
            print(f"⚠️  Current count ({current_count}) is less than target ({target_count})")
            print("This might indicate missing episodes in the source data")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error adjusting {series_name}: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    """Main function to adjust episode counts."""
    print("🎬 Adjusting Episode Counts to Match Actual Content")
    print("=" * 60)
    
    # Show current counts
    current_counts = get_current_episode_counts()
    
    print("📊 Current Episode Counts:")
    for series_name, count in current_counts.items():
        print(f"  • {series_name}: {count} episodes")
    
    print(f"\n🎯 Target Episode Counts:")
    for series_name, target_count in TARGET_EPISODE_COUNTS.items():
        current_count = current_counts.get(series_name, 0)
        status = "✅" if current_count == target_count else "⚠️"
        print(f"  {status} {series_name}: {current_count} → {target_count}")
    
    # Ask for confirmation
    print(f"\n❓ Do you want to proceed with these adjustments?")
    print("This will remove excess episodes to match your actual content.")
    
    # For now, proceed with Bonanza adjustment
    print(f"\n🔧 Starting with Bonanza adjustment...")
    adjust_episode_count('Bonanza', 13)
    
    # Show final counts
    print(f"\n📊 Final Episode Counts:")
    final_counts = get_current_episode_counts()
    for series_name, count in final_counts.items():
        print(f"  • {series_name}: {count} episodes")

if __name__ == "__main__":
    main() 