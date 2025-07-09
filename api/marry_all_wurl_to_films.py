#!/usr/bin/env python3
"""
Comprehensive script to marry WURL data to films from all available WURL metadata files.
Matches WURL artwork filenames to films in the database and updates poster URLs.
"""

import os
import sys
import csv
import glob
from pathlib import Path
import re
from sqlalchemy.orm import Session

# Add the current directory to Python path
sys.path.append('.')

from database import SessionLocal
from models import Content

def normalize_title(title):
    """Normalize title for matching by removing special characters and converting to lowercase"""
    if not title:
        return ""
    
    # Convert to lowercase
    title = title.lower()
    
    # Remove special characters and extra spaces
    title = re.sub(r'[^\w\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def get_films_from_database():
    """Get all films from the database"""
    db = SessionLocal()
    try:
        films = db.query(Content).filter(Content.type == "FILM").order_by(Content.title).all()
        
        film_data = []
        for film in films:
            film_data.append((
                film.id,
                film.title,
                film.poster_url,
                film.type
            ))
        
        print(f"🎬 Found {len(film_data)} films in database")
        return film_data
    finally:
        db.close()

def get_all_wurl_movies():
    """Get all movies from all WURL metadata files"""
    wurl_dir = Path("/Users/sdbmi/dev/pecantv_app")
    csv_files = list(wurl_dir.glob("Wurl - File Upload Metadata_Version 7.0.*.csv"))
    
    if not csv_files:
        print("❌ No WURL metadata files found")
        return []
    
    # Sort by version number
    def extract_version_number(filename):
        match = re.search(r'7\.0\.(\d+)', filename.name)
        return int(match.group(1)) if match else 0
    
    csv_files.sort(key=extract_version_number)
    print(f"📁 Found {len(csv_files)} WURL metadata files")
    
    all_movies = []
    processed_files = 0
    
    for csv_file in csv_files:
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            file_content = None
            
            for encoding in encodings:
                try:
                    with open(csv_file, 'r', encoding=encoding) as file:
                        file_content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if file_content is None:
                print(f"❌ Could not read {csv_file.name} with any encoding")
                continue
            
            # Parse CSV content
            reader = csv.DictReader(file_content.splitlines())
            
            for row in reader:
                # Check if this is a movie entry
                if row.get('Entry Type', '').strip() == 'Movie':
                    title = row.get('Title', '').strip()
                    artwork_filename = row.get('Artwork Filename', '').strip()
                    
                    if title and artwork_filename:
                        # Clean up artwork filename
                        if artwork_filename.endswith('.png'):
                            artwork_filename = artwork_filename[:-4]
                        elif artwork_filename.endswith('.jpg'):
                            artwork_filename = artwork_filename[:-4]
                        
                        all_movies.append({
                            'title': title,
                            'artwork_filename': artwork_filename,
                            'source_file': csv_file.name
                        })
        
        except Exception as e:
            print(f"❌ Error processing {csv_file.name}: {e}")
            continue
        
        processed_files += 1
        print(f"📄 Processed {csv_file.name}")
    
    print(f"🎬 Found {len(all_movies)} movies across {processed_files} WURL files")
    return all_movies

def find_matches(films, wurl_movies):
    """Find matches between films and WURL movies"""
    matches = []
    
    for film_id, title, poster_url, content_type in films:
        normalized_film_title = normalize_title(title)
        
        for wurl_movie in wurl_movies:
            normalized_wurl_title = normalize_title(wurl_movie['title'])
            
            # Check for exact match or close match
            if (normalized_film_title == normalized_wurl_title or 
                normalized_film_title in normalized_wurl_title or 
                normalized_wurl_title in normalized_film_title):
                
                # Construct new poster URL
                new_poster_url = f"/pecantv_series/{wurl_movie['artwork_filename']}.jpg"
                
                matches.append({
                    'id': film_id,
                    'title': title,
                    'old_poster_url': poster_url,
                    'new_poster_url': new_poster_url,
                    'artwork_file': wurl_movie['artwork_filename'],
                    'wurl_title': wurl_movie['title'],
                    'source_file': wurl_movie['source_file']
                })
                break  # Found a match, move to next film
    
    return matches

def update_film_posters(matches):
    """Update film poster URLs in the database"""
    if not matches:
        print("❌ No matches found to update")
        return
    
    db = SessionLocal()
    try:
        updated_count = 0
        for match in matches:
            try:
                film = db.query(Content).filter(Content.id == match['id']).first()
                if film:
                    film.poster_url = match['new_poster_url']
                    updated_count += 1
                    print(f"✅ Updated {match['title']} (ID: {match['id']})")
                    print(f"   WURL Title: {match['wurl_title']}")
                    print(f"   Source: {match['source_file']}")
                    print(f"   Old: {match['old_poster_url']}")
                    print(f"   New: {match['new_poster_url']}")
                    print()
                else:
                    print(f"❌ Film not found: {match['title']} (ID: {match['id']})")
            except Exception as e:
                print(f"❌ Error updating film {match['id']}: {e}")
        
        # Commit changes
        db.commit()
        print(f"🎉 Successfully updated {updated_count} film poster URLs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🎬 Comprehensive WURL to Films Marriage Script")
    print("=" * 60)
    
    # Get films from database
    films = get_films_from_database()
    if not films:
        print("❌ No films found in database")
        return
    
    # Get all WURL movies
    wurl_movies = get_all_wurl_movies()
    if not wurl_movies:
        print("❌ No WURL movies found")
        return
    
    # Find matches
    print("\n🔍 Finding matches between films and WURL movies...")
    matches = find_matches(films, wurl_movies)
    
    if not matches:
        print("❌ No matches found")
        return
    
    print(f"\n🎯 Found {len(matches)} potential matches:")
    for match in matches:
        print(f"   📺 {match['title']} (ID: {match['id']})")
        print(f"      WURL: {match['wurl_title']}")
        print(f"      Source: {match['source_file']}")
        print(f"      Artwork: {match['artwork_file']}")
        print()
    
    # Ask for confirmation
    response = input(f"❓ Update {len(matches)} film poster URLs? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Operation cancelled")
        return
    
    # Update posters
    update_film_posters(matches)

if __name__ == "__main__":
    main() 