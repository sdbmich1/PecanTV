#!/usr/bin/env python3
"""
Script to marry WURL data to films for homepage cleanup.
Matches WURL artwork filenames to films in the database and updates poster URLs.
"""

import os
import sys
import csv
from pathlib import Path
import re
from sqlalchemy.orm import Session

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

def get_wurl_artwork_files():
    """Get list of WURL artwork files from the latest metadata CSV file"""
    # Find the latest WURL metadata file
    metadata_dir = Path("/Users/sdbmi/dev/pecantv_app")
    csv_files = list(metadata_dir.glob("Wurl - File Upload Metadata_Version 7.0.*.csv"))
    
    if not csv_files:
        print("❌ No WURL metadata CSV files found")
        return []
    
    # Get the latest file (highest version number)
    def extract_version_number(filename):
        # Extract version number from filename like "Wurl - File Upload Metadata_Version 7.0.64.csv"
        match = re.search(r'7\.0\.(\d+)', filename.name)
        return int(match.group(1)) if match else 0
    
    latest_file = max(csv_files, key=extract_version_number)
    print(f"📁 Using WURL metadata file: {latest_file.name}")
    
    artwork_files = []
    try:
        with open(latest_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check if it's a movie and has artwork filename
                if (row.get('Entry Type') == 'Movie' and 
                    row.get('Artwork Filename') and 
                    row.get('Artwork Filename').strip()):
                    
                    # Extract filename without extension
                    artwork_filename = row['Artwork Filename'].strip()
                    if artwork_filename.endswith('.png'):
                        artwork_filename = artwork_filename[:-4]  # Remove .png extension
                    elif artwork_filename.endswith('.jpg'):
                        artwork_filename = artwork_filename[:-4]  # Remove .jpg extension
                    
                    artwork_files.append({
                        'title': row.get('Title', '').strip(),
                        'artwork_filename': artwork_filename,
                        'external_id': row.get('External ID', '').strip()
                    })
    except Exception as e:
        print(f"❌ Error reading WURL metadata: {e}")
        return []
    
    print(f"📁 Found {len(artwork_files)} WURL artwork entries")
    return artwork_files

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

def match_films_to_artwork(films, artwork_files):
    """Match films to artwork files and return matches"""
    matches = []
    unmatched_films = []
    
    for film_id, title, poster_url, content_type in films:
        normalized_title = normalize_title(title)
        
        # Try to find matching artwork file
        matched_artwork = None
        for artwork_entry in artwork_files:
            artwork_title = artwork_entry['title']
            artwork_filename = artwork_entry['artwork_filename']
            normalized_artwork_title = normalize_title(artwork_title)
            
            # Check for exact match or close match
            if normalized_title == normalized_artwork_title:
                matched_artwork = artwork_filename
                break
            elif normalized_title in normalized_artwork_title or normalized_artwork_title in normalized_title:
                matched_artwork = artwork_filename
                break
        
        if matched_artwork:
            # Construct new poster URL
            new_poster_url = f"/pecantv_series/{matched_artwork}.jpg"
            matches.append({
                'id': film_id,
                'title': title,
                'old_poster_url': poster_url,
                'new_poster_url': new_poster_url,
                'artwork_file': matched_artwork
            })
        else:
            unmatched_films.append({
                'id': film_id,
                'title': title,
                'poster_url': poster_url
            })
    
    return matches, unmatched_films

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
                    print(f"   Old: {match['old_poster_url']}")
                    print(f"   New: {match['new_poster_url']}")
                    print()
                else:
                    print(f"❌ Film not found: {match['title']} (ID: {match['id']})")
                    
            except Exception as e:
                print(f"❌ Error updating {match['title']}: {e}")
        
        db.commit()
        print(f"🎉 Successfully updated {updated_count} film poster URLs")
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🎬 Starting WURL to Films Marriage Process")
    print("=" * 50)
    
    # Get WURL artwork files
    artwork_files = get_wurl_artwork_files()
    if not artwork_files:
        return
    
    # Get films from database
    films = get_films_from_database()
    if not films:
        return
    
    # Match films to artwork
    print("\n🔍 Matching films to WURL artwork...")
    matches, unmatched_films = match_films_to_artwork(films, artwork_files)
    
    print(f"\n📊 Results:")
    print(f"   ✅ Matched: {len(matches)} films")
    print(f"   ❌ Unmatched: {len(unmatched_films)} films")
    
    if matches:
        print(f"\n🎯 Matches found:")
        for match in matches:
            print(f"   • {match['title']} → {match['artwork_file']}")
        
        # Ask for confirmation
        response = input(f"\n🤔 Update {len(matches)} film poster URLs? (y/N): ")
        if response.lower() in ['y', 'yes']:
            update_film_posters(matches)
        else:
            print("❌ Update cancelled")
    
    if unmatched_films:
        print(f"\n❌ Unmatched films ({len(unmatched_films)}):")
        for film in unmatched_films[:20]:  # Show first 20
            print(f"   • {film['title']} (ID: {film['id']})")
        
        if len(unmatched_films) > 20:
            print(f"   ... and {len(unmatched_films) - 20} more")
    
    print("\n✨ WURL to Films marriage process completed!")

if __name__ == "__main__":
    main() 