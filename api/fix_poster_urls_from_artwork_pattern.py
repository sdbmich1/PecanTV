#!/usr/bin/env python3
"""
Fix poster URLs based on the artwork filename pattern from series name and episode number
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def fix_poster_urls_from_artwork_pattern():
    """Fix poster URLs based on the artwork filename pattern"""
    
    with engine.begin() as conn:
        print("🔧 Fixing poster URLs based on artwork filename pattern...")
        print("=" * 60)
        
        # 1. Fix series posters (content with series_name but no episode_number)
        print("📺 1. Fixing series posters...")
        result = conn.execute(text("""
            SELECT id, title, series_name, poster_url 
            FROM content 
            WHERE series_name IS NOT NULL 
            AND episode_number IS NULL
            AND type = 'SERIES'
        """))
        
        series_content = result.fetchall()
        print(f"Found {len(series_content)} series to fix")
        
        for content_id, title, series_name, current_poster in series_content:
            # Use the first episode's poster as the series poster
            # Format: [SeriesName]1_poster.jpg
            series_poster = f"{series_name}1_poster.jpg"
            new_poster_url = f"http://localhost:8000/pecantv_series/{series_name.lower().replace(' ', '_')}/{series_poster}"
            
            conn.execute(text("""
                UPDATE content 
                SET poster_url = :new_url
                WHERE id = :content_id
            """), {
                'new_url': new_poster_url,
                'content_id': content_id
            })
            print(f"  Fixed {title}: {new_poster_url}")
        
        # 2. Fix episode posters (content with both series_name and episode_number)
        print("\n📺 2. Fixing episode posters...")
        result = conn.execute(text("""
            SELECT id, title, series_name, episode_number, poster_url 
            FROM content 
            WHERE series_name IS NOT NULL 
            AND episode_number IS NOT NULL
        """))
        
        episode_content = result.fetchall()
        print(f"Found {len(episode_content)} episodes to fix")
        
        for content_id, title, series_name, episode_number, current_poster in episode_content:
            # Format: [SeriesName][EpisodeNumber]_poster.jpg
            episode_poster = f"{series_name}{episode_number}_poster.jpg"
            new_poster_url = f"http://localhost:8000/pecantv_series/{series_name.lower().replace(' ', '_')}/{episode_poster}"
            
            conn.execute(text("""
                UPDATE content 
                SET poster_url = :new_url
                WHERE id = :content_id
            """), {
                'new_url': new_poster_url,
                'content_id': content_id
            })
            print(f"  Fixed {title} (Episode {episode_number}): {new_poster_url}")
        
        # 3. Fix films (content with type = 'FILM')
        print("\n📺 3. Fixing film posters...")
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE type = 'FILM'
        """))
        
        film_content = result.fetchall()
        print(f"Found {len(film_content)} films to fix")
        
        for content_id, title, current_poster in film_content:
            # For films, use a default poster or the title as filename
            film_filename = title.lower().replace(' ', '_').replace(':', '').replace('-', '_')
            new_poster_url = f"http://localhost:8000/pecantv_series/{film_filename}/poster.jpg"
            
            conn.execute(text("""
                UPDATE content 
                SET poster_url = :new_url
                WHERE id = :content_id
            """), {
                'new_url': new_poster_url,
                'content_id': content_id
            })
            print(f"  Fixed {title}: {new_poster_url}")
        
        # 4. Verify the fixes
        print("\n🔍 Verifying fixes...")
        
        # Check Dragnet series
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE id = 68
        """))
        
        dragnet = result.fetchone()
        if dragnet:
            title, poster_url = dragnet
            print(f"Dragnet series poster: {poster_url}")
        
        # Check Dragnet episode 1
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE series_name = 'Dragnet' AND episode_number = 1
        """))
        
        dragnet_ep1 = result.fetchone()
        if dragnet_ep1:
            title, poster_url = dragnet_ep1
            print(f"Dragnet episode 1 poster: {poster_url}")
        
        # Check Christie Love
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE id = 3
        """))
        
        christie_love = result.fetchone()
        if christie_love:
            title, poster_url = christie_love
            print(f"Christie Love poster: {poster_url}")
        
        # Check some sample content
        result = conn.execute(text("""
            SELECT title, poster_url 
            FROM content 
            WHERE poster_url IS NOT NULL 
            AND poster_url != ''
            LIMIT 5
        """))
        
        sample_content = result.fetchall()
        print(f"Sample content with posters ({len(sample_content)}):")
        for title, poster_url in sample_content:
            print(f"  {title}: {poster_url}")
        
        print("\n✅ All poster URLs fixed based on artwork filename pattern!")

if __name__ == "__main__":
    fix_poster_urls_from_artwork_pattern() 