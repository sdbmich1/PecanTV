#!/usr/bin/env python3
"""
Script to fix final Bonanza URL issues:
1. Keep only episodes 1-13
2. Fix incomplete URLs (missing .mp4 extension)
3. Standardize URL patterns to use pecantv_series/bonanza/
4. Fix poster URLs to use consistent pattern
"""

import psycopg2
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

def fix_bonanza_episodes():
    """Fix Bonanza episodes to have exactly 13 episodes with correct URLs."""
    print("🔧 Fixing Bonanza Episodes - Final Cleanup")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # Get Bonanza series ID
        cur.execute("SELECT id FROM content WHERE title = 'Bonanza' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Bonanza series not found")
            return
        
        series_id = series_result[0]
        print(f"✅ Found Bonanza series (ID: {series_id})")
        
        # First, let's see what we have
        cur.execute("""
            SELECT id, title, season_number, episode_number, content_url, poster_url
            FROM episodes 
            WHERE series_id = %s
            ORDER BY episode_number
        """, (series_id,))
        
        all_episodes = cur.fetchall()
        print(f"\n📺 Found {len(all_episodes)} total Bonanza episodes")
        
        # Keep only episodes 1-13
        episodes_to_keep = []
        for ep_id, title, season, episode, content_url, poster_url in all_episodes:
            if episode <= 13:
                episodes_to_keep.append((ep_id, title, season, episode, content_url, poster_url))
            else:
                # Delete episodes beyond 13
                cur.execute("DELETE FROM episodes WHERE id = %s", (ep_id,))
                print(f"  🗑️  Deleted episode {episode}: {title}")
        
        print(f"\n✅ Kept {len(episodes_to_keep)} episodes (1-13)")
        
        # Fix URLs for the remaining episodes
        fixed_count = 0
        for ep_id, title, season, episode, content_url, poster_url in episodes_to_keep:
            print(f"\n🔧 Fixing episode {episode}: {title}")
            
            # Fix content URL
            new_content_url = content_url
            if content_url:
                # Fix incomplete URLs (missing .mp4 extension)
                if content_url.endswith('wCredits') and not content_url.endswith('.mp4'):
                    new_content_url = content_url + '.mp4'
                    print(f"     Fixed content URL: {new_content_url}")
                
                # Standardize to pecantv_series/bonanza/ pattern
                if 'pecantv_features/' in new_content_url:
                    new_content_url = new_content_url.replace('pecantv_features/', 'pecantv_series/bonanza/')
                    print(f"     Standardized content URL: {new_content_url}")
            
            # Fix poster URL
            new_poster_url = poster_url
            if poster_url:
                # Standardize to pecantv_series/bonanza/ pattern
                if 'pecantv_features/' in new_poster_url:
                    new_poster_url = new_poster_url.replace('pecantv_features/', 'pecantv_series/bonanza/')
                    print(f"     Standardized poster URL: {new_poster_url}")
            
            # Update the episode
            cur.execute("""
                UPDATE episodes 
                SET content_url = %s, poster_url = %s, updated_at = %s
                WHERE id = %s
            """, (new_content_url, new_poster_url, datetime.now(timezone.utc), ep_id))
            
            fixed_count += 1
        
        conn.commit()
        print(f"\n✅ Successfully fixed {fixed_count} Bonanza episodes!")
        
        # Verify final status
        print("\n📊 Final Verification:")
        print("-" * 30)
        cur.execute("""
            SELECT id, title, episode_number, content_url, poster_url
            FROM episodes 
            WHERE series_id = %s
            ORDER BY episode_number
        """, (series_id,))
        
        final_episodes = cur.fetchall()
        print(f"  Total episodes: {len(final_episodes)}")
        
        for ep_id, title, episode, content_url, poster_url in final_episodes:
            content_status = "✅" if content_url and content_url.endswith('.mp4') else "❌"
            poster_status = "✅" if poster_url and 'pecantv_series/bonanza/' in poster_url else "❌"
            
            print(f"  {content_status} S1E{episode:02d} - {title}")
            print(f"     Content: {content_url}")
            print(f"     Poster: {poster_url}")
        
        if len(final_episodes) == 13:
            print(f"\n🎉 SUCCESS: Exactly 13 Bonanza episodes with correct URLs!")
        else:
            print(f"\n⚠️  WARNING: Expected 13 episodes, found {len(final_episodes)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_bonanza_episodes() 