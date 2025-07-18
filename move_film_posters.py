#!/usr/bin/env python3
"""
Move film posters to the root of pecantv_series directory for better accessibility
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "api"))

from database import engine
from sqlalchemy import text
import shutil

def move_film_posters():
    """Move film posters to root of pecantv_series directory"""
    
    with engine.begin() as conn:
        print("🎬 Moving film posters to root of pecantv_series directory...")
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
        
        # Move film posters from films subdirectory to root
        films_dir = Path("pecantv_series/films")
        root_dir = Path("pecantv_series")
        
        if films_dir.exists():
            for film in films:
                # Create a unique filename for each film
                film_title = film.title.replace(" ", "_").replace(":", "").replace("'", "").replace("-", "_").replace(".", "")
                old_poster_path = films_dir / f"{film_title}_poster.jpg"
                new_poster_path = root_dir / f"{film_title}_poster.jpg"
                
                # Move the poster file
                if old_poster_path.exists():
                    shutil.move(str(old_poster_path), str(new_poster_path))
                    print(f"✅ Moved {film.title}: {old_poster_path.name} -> {new_poster_path.name}")
        
        # Now update the database with the new poster URLs
        print(f"\n📝 Updating database with new film poster URLs...")
        
        for film in films:
            film_title = film.title.replace(" ", "_").replace(":", "").replace("'", "").replace("-", "_").replace(".", "")
            poster_url = f"{railway_url}/pecantv_series/{film_title}_poster.jpg"
            
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
        
        # Remove the empty films directory
        if films_dir.exists() and not any(films_dir.iterdir()):
            films_dir.rmdir()
            print(f"🗑️  Removed empty films directory")
        
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
        
        print(f"\n🎉 Film poster URLs updated!")
        print(f"📁 Moved {len(films)} poster files to root directory")
        print(f"🌐 All film poster URLs now point to Railway deployment")
        
        return True

if __name__ == "__main__":
    move_film_posters() 