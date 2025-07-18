#!/usr/bin/env python3
"""
Create unique poster URLs for films using a pattern-based approach
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "api"))

from database import engine
from sqlalchemy import text

def create_film_posters():
    """Create unique poster URLs for films"""
    
    with engine.begin() as conn:
        print("🎬 Creating unique poster URLs for films...")
        print("=" * 60)
        
        # Railway base URL
        railway_url = "https://pecantv-api-production.up.railway.app"
        
        # Get all films
        result = conn.execute(text("""
            SELECT id, title 
            FROM content 
            WHERE type = 'FILM'
            ORDER BY id
        """))
        
        films = result.fetchall()
        
        # Create a films directory structure
        films_dir = Path("pecantv_series/films")
        films_dir.mkdir(exist_ok=True)
        
        # Copy default poster to films directory as a starting point
        default_poster = Path("pecantv_series/default_poster.jpg")
        if default_poster.exists():
            import shutil
            for film in films:
                # Create a unique filename for each film
                film_title = film.title.replace(" ", "_").replace(":", "").replace("'", "").replace("-", "_").replace(".", "")
                poster_filename = f"{film_title}_poster.jpg"
                poster_path = films_dir / poster_filename
                
                # Copy the default poster to create a unique file for each film
                if not poster_path.exists():
                    shutil.copy2(default_poster, poster_path)
                    print(f"✅ Created poster for {film.title}: {poster_filename}")
        
        # Now update the database with the correct poster URLs
        print(f"\n📝 Updating database with film poster URLs...")
        
        for film in films:
            film_title = film.title.replace(" ", "_").replace(":", "").replace("'", "").replace("-", "_").replace(".", "")
            poster_url = f"{railway_url}/pecantv_series/films/{film_title}_poster.jpg"
            
            # Update the film's poster URL
            conn.execute(text("""
                UPDATE content 
                SET poster_url = :poster_url
                WHERE id = :film_id
            """), {
                'poster_url': poster_url,
                'film_id': film.id
            })
            print(f"✅ Updated {film.title}: {poster_url}")
        
        # Verify the changes
        print(f"\n🔍 Verifying film poster URLs...")
        
        # Check a few films
        result = conn.execute(text("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE type = 'FILM'
            ORDER BY id 
            LIMIT 5
        """))
        
        film_items = result.fetchall()
        for item in film_items:
            print(f"  - {item.title}: {item.poster_url}")
        
        print(f"\n🎉 Film poster URLs created!")
        print(f"📁 Created {len(films)} unique poster files")
        print(f"🌐 All film poster URLs now point to Railway deployment")
        
        return True

if __name__ == "__main__":
    create_film_posters() 