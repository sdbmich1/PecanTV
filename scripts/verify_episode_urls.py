#!/usr/bin/env python3
"""
Script to verify that all episodes have contentURL set correctly and posterURL is used for display only.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def verify_episode_urls():
    """Verify that all episodes have contentURL set and posterURL is for display only."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Verifying Episode URL Fields in Database")
        print("=" * 60)
        
        # Get all episodes with their URL fields
        cur.execute("""
            SELECT e.id, e.title, e.content_url, e.poster_url, c.title as series_title
            FROM episodes e
            JOIN content c ON e.series_id = c.id
            ORDER BY c.title, e.season_number, e.episode_number
        """)
        
        episodes = cur.fetchall()
        
        print(f"📊 Total episodes found: {len(episodes)}")
        print()
        
        # Group by series for better analysis
        series_data = {}
        for ep in episodes:
            series = ep['series_title']
            if series not in series_data:
                series_data[series] = []
            series_data[series].append(ep)
        
        # Analyze each series
        for series_name, series_episodes in series_data.items():
            print(f"🎬 Series: {series_name} ({len(series_episodes)} episodes)")
            print("-" * 40)
            
            # Check contentURL patterns
            content_urls = [ep['content_url'] for ep in series_episodes if ep['content_url']]
            poster_urls = [ep['poster_url'] for ep in series_episodes if ep['poster_url']]
            
            # Check if contentURLs are unique per episode
            unique_content_urls = len(set(content_urls))
            unique_poster_urls = len(set(poster_urls))
            
            print(f"  ✅ ContentURLs: {len(content_urls)}/{len(series_episodes)} episodes have contentURL")
            print(f"  📊 Unique contentURLs: {unique_content_urls} (should be {len(series_episodes)} for unique episodes)")
            print(f"  🖼️  Unique posterURLs: {unique_poster_urls} (can be shared)")
            
            # Check for missing contentURLs
            missing_content = [ep for ep in series_episodes if not ep['content_url']]
            if missing_content:
                print(f"  ❌ Missing contentURL: {len(missing_content)} episodes")
                for ep in missing_content[:3]:  # Show first 3
                    print(f"     - {ep['title']}")
                if len(missing_content) > 3:
                    print(f"     ... and {len(missing_content) - 3} more")
            
            # Show sample URLs
            if series_episodes:
                sample_ep = series_episodes[0]
                print(f"  📝 Sample contentURL: {sample_ep['content_url']}")
                print(f"  🖼️  Sample posterURL: {sample_ep['poster_url']}")
            
            print()
        
        # Summary statistics
        print("📈 SUMMARY")
        print("=" * 60)
        total_episodes = len(episodes)
        episodes_with_content = len([ep for ep in episodes if ep['content_url']])
        episodes_with_poster = len([ep for ep in episodes if ep['poster_url']])
        
        print(f"Total episodes: {total_episodes}")
        print(f"Episodes with contentURL: {episodes_with_content} ({episodes_with_content/total_episodes*100:.1f}%)")
        print(f"Episodes with posterURL: {episodes_with_poster} ({episodes_with_poster/total_episodes*100:.1f}%)")
        
        if episodes_with_content == total_episodes:
            print("✅ All episodes have contentURL set correctly!")
        else:
            print(f"❌ {total_episodes - episodes_with_content} episodes missing contentURL")
        
        # Check for duplicate contentURLs (should be unique per episode)
        all_content_urls = [ep['content_url'] for ep in episodes if ep['content_url']]
        unique_content_urls = set(all_content_urls)
        if len(all_content_urls) == len(unique_content_urls):
            print("✅ All contentURLs are unique (as expected for episodes)")
        else:
            print(f"⚠️  {len(all_content_urls) - len(unique_content_urls)} duplicate contentURLs found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    verify_episode_urls() 