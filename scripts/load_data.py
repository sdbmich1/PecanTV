import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API setup
SPREADSHEET_ID = '1ZmUOUX9euUWc6qcLs8H2AFvf3neGEM7uppdKsh0Hj-E'
SHEET_TABS = {
    'content': 'Content',
    'genres': 'Genres',
    'ratings': 'Ratings'
}
SERVICE_ACCOUNT_FILE = 'pecantv-f585e-6fe7a40a0bea.json'

# Database connection parameters
DB_PARAMS = {
    'dbname': 'pecantv',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',  # Local connection
    'port': '5433'        # Docker port mapping
}

def load_data_from_sheets():
    """Load data from Google Sheets using gspread and service account."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    data = {}
    for key, tab in SHEET_TABS.items():
        worksheet = sheet.worksheet(tab)
        records = worksheet.get_all_records()
        data[key] = pd.DataFrame(records)
    return data

def insert_genres(conn, genres_df):
    """Insert genres into the database."""
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO genres (name, description)
            VALUES %s
            ON CONFLICT (name) DO UPDATE
            SET description = EXCLUDED.description
            """,
            [(row['name'], row.get('description', '')) for _, row in genres_df.iterrows()]
        )
    conn.commit()

def insert_ratings(conn, ratings_df):
    """Insert ratings into the database."""
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO ratings (code, description, min_age)
            VALUES %s
            ON CONFLICT (code) DO UPDATE
            SET description = EXCLUDED.description,
                min_age = EXCLUDED.min_age
            """,
            [(row['code'], row.get('description', ''), row.get('min_age')) 
             for _, row in ratings_df.iterrows()]
        )
    conn.commit()

def insert_content(conn, content_df, genre_map, rating_map):
    """Insert content into the database."""
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO content (
                title, poster_url, trailer_url, content_url,
                description, type, runtime, genre_id, rating_id,
                release_date
            )
            VALUES %s
            ON CONFLICT (title) DO UPDATE
            SET poster_url = EXCLUDED.poster_url,
                trailer_url = EXCLUDED.trailer_url,
                content_url = EXCLUDED.content_url,
                description = EXCLUDED.description,
                type = EXCLUDED.type,
                runtime = EXCLUDED.runtime,
                genre_id = EXCLUDED.genre_id,
                rating_id = EXCLUDED.rating_id,
                release_date = EXCLUDED.release_date
            """,
            [(
                row['title'],
                row['poster_url'],
                row['trailer_url'],
                row['content_url'],
                row.get('description', ''),
                row['type'].upper(),
                int(row['runtime']),
                genre_map.get(row['genre']),
                rating_map.get(row['rating']),
                pd.to_datetime(row.get('release_date')).date() if pd.notna(row.get('release_date')) else None
            ) for _, row in content_df.iterrows()]
        )
    conn.commit()

def get_id_maps(conn):
    """Get maps of names to IDs for genres and ratings."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM genres")
        genre_map = {row[1]: row[0] for row in cur.fetchall()}
        
        cur.execute("SELECT id, code FROM ratings")
        rating_map = {row[1]: row[0] for row in cur.fetchall()}
    
    return genre_map, rating_map

def main():
    # Load data from Google Sheets
    print("Loading data from Google Sheets...")
    data = load_data_from_sheets()
    
    # Connect to PostgreSQL
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_PARAMS)
    
    try:
        # Insert genres
        print("Inserting genres...")
        insert_genres(conn, data['genres'])
        
        # Insert ratings
        print("Inserting ratings...")
        insert_ratings(conn, data['ratings'])
        
        # Get ID maps
        genre_map, rating_map = get_id_maps(conn)
        
        # Insert content
        print("Inserting content...")
        insert_content(conn, data['content'], genre_map, rating_map)
        
        print("Data import completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main() 