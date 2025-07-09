#!/usr/bin/env python3
"""
Script to match WURL artwork filenames to films in the database and update their poster_url fields.
"""

import psycopg2
import pandas as pd
import glob
import re

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# GCS base URL for posters
GCS_BASE = 'https://storage.googleapis.com/pecantv_title_images/'

def load_wurl_film_data():
    """Load film data from all WURL metadata files."""
    files = glob.glob('Wurl*.xlsx')
    all_films = []
    for file in files:
        try:
            df = pd.read_excel(file)
            if 'Title' in df.columns and 'Artwork Filename' in df.columns and 'Series Name' in df.columns:
                films = df[(df['Series Name'].isna() | (df['Series Name'] == '')) & df['Artwork Filename'].notna()]
                for _, row in films.iterrows():
                    all_films.append({
                        'title': str(row['Title']).strip(),
                        'artwork_filename': str(row['Artwork Filename']).strip()
                    })
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return all_films

def main():
    print("Loading WURL film data...")
    wurl_films = load_wurl_film_data()
    wurl_map = {f['title'].lower(): f['artwork_filename'] for f in wurl_films if f['artwork_filename']}
    print(f"Loaded {len(wurl_map)} films from WURL metadata.")

    print("Connecting to database...")
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("SELECT id, title, poster_url FROM content WHERE type = 'FILM'")
    films = cur.fetchall()

    updated = 0
    unmatched = []
    for film_id, title, old_poster in films:
        key = title.lower().strip()
        if key in wurl_map:
            new_poster_url = GCS_BASE + wurl_map[key]
            if old_poster != new_poster_url:
                cur.execute("UPDATE content SET poster_url = %s WHERE id = %s", (new_poster_url, film_id))
                print(f"Updated {title} (ID {film_id}) poster to {new_poster_url}")
                updated += 1
        else:
            unmatched.append((film_id, title))

    conn.commit()
    print(f"\nUpdated {updated} film poster URLs.")
    if unmatched:
        print(f"\nFilms not matched to WURL artwork:")
        for film_id, title in unmatched:
            print(f"  ID {film_id}: {title}")
    else:
        print("All films matched!")
    conn.close()

if __name__ == "__main__":
    main() 