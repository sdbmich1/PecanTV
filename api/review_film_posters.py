#!/usr/bin/env python3
"""
Script to review film poster mappings and identify issues.
Prints ID, title, and poster_url for manual review.
"""

import sys
from sqlalchemy.orm import Session

# Add the current directory to Python path
sys.path.append('.')

from database import SessionLocal
from models import Content

def get_films_with_posters():
    """Get all films with their poster URLs for review"""
    db = SessionLocal()
    try:
        films = db.query(Content).filter(Content.type == "FILM").order_by(Content.id).all()
        
        film_data = []
        for film in films:
            film_data.append({
                'id': film.id,
                'title': film.title,
                'poster_url': film.poster_url,
                'type': film.type
            })
        
        print(f"🎬 Found {len(film_data)} films in database")
        return film_data
    finally:
        db.close()

def analyze_poster_issues(films):
    """Analyze films for poster-related issues"""
    issues = {
        'google_cloud_storage': [],
        'default_posters': [],
        'missing_posters': [],
        'potential_mismatches': [],
        'local_posters': []
    }
    
    for film in films:
        poster_url = film['poster_url']
        
        if not poster_url:
            issues['missing_posters'].append(film)
        elif 'storage.googleapis.com' in poster_url:
            issues['google_cloud_storage'].append(film)
        elif 'default_poster' in poster_url:
            issues['default_posters'].append(film)
        elif poster_url.startswith('/pecantv_series/'):
            issues['local_posters'].append(film)
            
            # Check for potential mismatches (poster filename doesn't match title)
            poster_filename = poster_url.split('/')[-1].replace('.jpg', '').replace('.png', '')
            title_words = film['title'].lower().split()
            
            # Simple mismatch detection
            title_in_poster = any(word in poster_filename.lower() for word in title_words if len(word) > 2)
            if not title_in_poster and len(poster_filename) > 5:
                issues['potential_mismatches'].append(film)
    
    return issues

def print_film_review(films, issues):
    """Print comprehensive film poster review"""
    print("🎬 Film Poster Review Report")
    print("=" * 80)
    print(f"Total Films: {len(films)}")
    print()
    
    # Summary
    print("📊 SUMMARY:")
    print(f"  • Local Posters: {len(issues['local_posters'])}")
    print(f"  • Google Cloud Storage: {len(issues['google_cloud_storage'])}")
    print(f"  • Default Posters: {len(issues['default_posters'])}")
    print(f"  • Missing Posters: {len(issues['missing_posters'])}")
    print(f"  • Potential Mismatches: {len(issues['potential_mismatches'])}")
    print()
    
    # All films (for manual review)
    print("📋 ALL FILMS (ID | Title | Poster URL):")
    print("-" * 80)
    for film in films:
        print(f"{film['id']:3d} | {film['title']:<40} | {film['poster_url']}")
    print()
    
    # Potential mismatches
    if issues['potential_mismatches']:
        print("⚠️  POTENTIAL MISMATCHES (Review these carefully):")
        print("-" * 80)
        for film in issues['potential_mismatches']:
            poster_filename = film['poster_url'].split('/')[-1].replace('.jpg', '').replace('.png', '')
            print(f"{film['id']:3d} | {film['title']:<40} | {film['poster_url']}")
            print(f"     Poster filename: {poster_filename}")
            print()
    
    # Google Cloud Storage URLs (need local conversion)
    if issues['google_cloud_storage']:
        print("🌐 GOOGLE CLOUD STORAGE URLs (need local conversion):")
        print("-" * 80)
        for film in issues['google_cloud_storage']:
            print(f"{film['id']:3d} | {film['title']:<40} | {film['poster_url']}")
        print()
    
    # Default posters (generic placeholders)
    if issues['default_posters']:
        print("🖼️  DEFAULT POSTERS (generic placeholders):")
        print("-" * 80)
        for film in issues['default_posters']:
            print(f"{film['id']:3d} | {film['title']:<40} | {film['poster_url']}")
        print()
    
    # Missing posters
    if issues['missing_posters']:
        print("❌ MISSING POSTERS:")
        print("-" * 80)
        for film in issues['missing_posters']:
            print(f"{film['id']:3d} | {film['title']:<40} | {film['poster_url']}")
        print()

def export_to_csv(films, filename="film_poster_review.csv"):
    """Export film data to CSV for external review"""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Title', 'Poster_URL', 'Type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for film in films:
            writer.writerow({
                'ID': film['id'],
                'Title': film['title'],
                'Poster_URL': film['poster_url'],
                'Type': film['type']
            })
    
    print(f"📄 Exported to {filename}")

def main():
    print("🔍 Film Poster Review Script")
    print("=" * 50)
    
    # Get films from database
    films = get_films_with_posters()
    if not films:
        print("❌ No films found in database")
        return
    
    # Analyze issues
    issues = analyze_poster_issues(films)
    
    # Print review
    print_film_review(films, issues)
    
    # Export to CSV
    export_to_csv(films)
    
    print("✅ Review complete! Check the CSV file for external analysis.")

if __name__ == "__main__":
    main() 