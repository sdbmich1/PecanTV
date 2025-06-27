#!/usr/bin/env python3
"""
Script to verify the current state of Petrocelli episodes in the database.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def test_url_exists(url):
    """Test if a URL returns a 200 status."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def verify_petrocelli_episodes():
    """Verify the current state of Petrocelli episodes."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 VERIFYING PETROCELLI EPISODES")
        print("=" * 60)
        
        # Get Petrocelli series ID
        cur.execute("SELECT id, title FROM content WHERE title = 'Petrocelli' AND type = 'SERIES'")
        series_result = cur.fetchone()
        if not series_result:
            print("❌ Petrocelli series not found")
            return
        
        series_id = series_result['id']
        print(f"✅ Found series: {series_result['title']} (ID: {series_id})")
        
        # Get all episodes with full details
        cur.execute("""
            SELECT 
                id,
                episode_number,
                title,
                description,
                content_url,
                poster_url,
                runtime,
                air_date,
                created_at,
                updated_at
            FROM episodes 
            WHERE series_id = %s 
            ORDER BY episode_number
        """, (series_id,))
        
        episodes = cur.fetchall()
        print(f"\n📺 Found {len(episodes)} episodes in database")
        print("\n" + "=" * 100)
        print(f"{'Ep#':<4} {'Title':<30} {'Content URL':<50} {'Status':<10}")
        print("=" * 100)
        
        working_episodes = 0
        placeholder_episodes = 0
        broken_episodes = 0
        
        for ep in episodes:
            episode_num = ep['episode_number']
            title = ep['title']
            content_url = ep['content_url']
            
            # Check for placeholder URLs
            is_placeholder = False
            if content_url and any(placeholder in content_url.lower() for placeholder in [
                'placeholder', 'not_available', 'fake', 'dummy', 'temp'
            ]):
                is_placeholder = True
                placeholder_episodes += 1
                status = "PLACEHOLDER"
            elif content_url and test_url_exists(content_url):
                working_episodes += 1
                status = "WORKING"
            else:
                broken_episodes += 1
                status = "BROKEN"
            
            # Truncate URL for display
            display_url = content_url[:47] + "..." if content_url and len(content_url) > 50 else content_url or "NULL"
            
            print(f"{episode_num:<4} {title:<30} {display_url:<50} {status:<10}")
        
        print("=" * 100)
        print(f"\n📊 SUMMARY:")
        print(f"Total episodes: {len(episodes)}")
        print(f"Working episodes: {working_episodes}")
        print(f"Placeholder episodes: {placeholder_episodes}")
        print(f"Broken episodes: {broken_episodes}")
        
        # Check for fake titles
        print(f"\n🔍 TITLE ANALYSIS:")
        fake_title_count = 0
        for ep in episodes:
            title = ep['title']
            if any(fake in title.lower() for fake in [
                'petrocelli episode', 'episode', 'placeholder', 'fake', 'dummy', 'temp'
            ]):
                fake_title_count += 1
                print(f"  ⚠️  Episode {ep['episode_number']}: '{title}' (suspicious title)")
        
        if fake_title_count == 0:
            print("  ✅ No suspicious titles found")
        else:
            print(f"  ❌ Found {fake_title_count} episodes with suspicious titles")
        
        # Show detailed content URLs
        print(f"\n🔗 CONTENT URL DETAILS:")
        for ep in episodes:
            episode_num = ep['episode_number']
            content_url = ep['content_url']
            if content_url:
                print(f"  Episode {episode_num}: {content_url}")
            else:
                print(f"  Episode {episode_num}: NULL content_url")
        
        return {
            'total': len(episodes),
            'working': working_episodes,
            'placeholder': placeholder_episodes,
            'broken': broken_episodes,
            'fake_titles': fake_title_count
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    result = verify_petrocelli_episodes() 