#!/usr/bin/env python3
"""
Remove only Dragnet episodes 1 and 3 that don't have video files
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def remove_missing_dragnet_episodes():
    """Remove only Dragnet episodes 1 and 3 that don't have video files"""
    
    with engine.connect() as conn:
        print("🔧 Removing Dragnet episodes 1 and 3 that don't have video files...")
        print("=" * 60)
        
        # First, check what episodes exist
        print("📋 Current Dragnet episodes:")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 
            ORDER BY episode_number
        """))
        
        dragnet_episodes = result.fetchall()
        print(f"Found {len(dragnet_episodes)} Dragnet episodes")
        
        for episode_id, episode_num, title, content_url in dragnet_episodes:
            print(f"Episode {episode_num}: {title}")
        
        # Remove episodes 1 and 3 that don't have video files
        print("\n🗑️ Removing episodes 1 and 3...")
        result = conn.execute(text("""
            DELETE FROM episodes 
            WHERE series_id = 68 AND episode_number IN (1, 3)
        """))
        
        deleted_count = result.rowcount
        print(f"Deleted {deleted_count} episodes")
        
        # Renumber the remaining episodes to be sequential
        print("\n📝 Renumbering remaining episodes to be sequential...")
        
        # Get remaining episodes
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 
            ORDER BY episode_number
        """))
        
        remaining_episodes = result.fetchall()
        
        # Update episode numbers to be sequential
        for i, (episode_id, old_episode_num, title, content_url) in enumerate(remaining_episodes, 1):
            conn.execute(text("""
                UPDATE episodes 
                SET episode_number = :new_number, 
                    title = :new_title
                WHERE id = :episode_id
            """), {
                'new_number': i,
                'new_title': f'Dragnet Animated - Episode {i}',
                'episode_id': episode_id
            })
        
        print(f"✅ Renumbered {len(remaining_episodes)} episodes")
        
        # Verify the changes
        print("\n🔍 Verifying changes...")
        result = conn.execute(text("""
            SELECT id, episode_number, title, content_url 
            FROM episodes 
            WHERE series_id = 68 
            ORDER BY episode_number
        """))
        
        final_episodes = result.fetchall()
        print(f"Found {len(final_episodes)} Dragnet episodes after fix")
        
        for episode_id, episode_num, title, content_url in final_episodes:
            filename = content_url.split('/')[-1] if content_url else "No URL"
            print(f"Episode {episode_num}: {title}")
            print(f"  URL: {content_url}")
            print(f"  Filename: {filename}")
            print()
        
        print("✅ Dragnet episodes fixed! Removed episodes 1 and 3, renumbered the rest.")

if __name__ == "__main__":
    remove_missing_dragnet_episodes() 