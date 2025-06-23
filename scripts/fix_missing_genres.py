#!/usr/bin/env python3
"""
Script to fix missing genres for content items.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database connection parameters
DB_PARAMS = {
    'dbname': 'pecantv',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5433'
}

def get_genre_id(conn, genre_name):
    """Get genre ID by name."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id FROM genres WHERE name = %s", (genre_name,))
        result = cur.fetchone()
        return result['id'] if result else None

def assign_genre_to_content(conn, content_id, genre_id):
    """Assign a genre to content."""
    with conn.cursor() as cur:
        # First, remove any existing genre assignment
        cur.execute("DELETE FROM content_genres WHERE content_id = %s", (content_id,))
        
        # Add the new genre assignment
        cur.execute("""
            INSERT INTO content_genres (content_id, genre_id)
            VALUES (%s, %s)
        """, (content_id, genre_id))
        
        conn.commit()

def fix_missing_genres():
    """Fix missing genres for content items."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Connected to database successfully.")
        
        # Get all content without genres
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT c.id, c.title, c.description
                FROM content c
                LEFT JOIN content_genres cg ON c.id = cg.content_id
                WHERE cg.content_id IS NULL
                ORDER BY c.title
            """)
            
            content_without_genres = cur.fetchall()
        
        print(f"Found {len(content_without_genres)} content items without genres.")
        
        # Genre mapping based on title keywords
        genre_mapping = {
            'christie love': 'Crime',
            'love': 'Drama',
            'detective': 'Crime',
            'police': 'Crime',
            'cop': 'Crime',
            'murder': 'Crime',
            'mystery': 'Crime',
            'action': 'Action',
            'adventure': 'Adventure',
            'comedy': 'Comedy',
            'drama': 'Drama',
            'horror': 'Horror',
            'sci-fi': 'Science Fiction',
            'science fiction': 'Science Fiction',
            'fantasy': 'Fantasy',
            'romance': 'Romance',
            'thriller': 'Thriller',
            'western': 'Western',
            'war': 'War',
            'documentary': 'Documentary',
            'educational': 'Educational',
            'children': 'Children',
            'family': 'Family',
            'animation': 'Animation',
            'anime': 'Anime',
            'sports': 'Sports',
            'music': 'Music',
            'food': 'Food',
            'travel': 'Travel',
            'nature': 'Nature',
            'wildlife': 'Animals',
            'animals': 'Animals',
            'history': 'History',
            'biography': 'Biography',
            'faith': 'Faith',
            'religious': 'Faith',
            'gaming': 'Gaming',
            'fashion': 'Fashion',
            'health': 'Health',
            'fitness': 'Health'
        }
        
        # Get genre IDs
        genre_ids = {}
        for genre_name in set(genre_mapping.values()):
            genre_id = get_genre_id(conn, genre_name)
            if genre_id:
                genre_ids[genre_name] = genre_id
            else:
                print(f"Warning: Genre '{genre_name}' not found in database")
        
        fixed_count = 0
        
        for content in content_without_genres:
            title_lower = content['title'].lower()
            description_lower = (content['description'] or '').lower()
            
            # Find matching genre
            assigned_genre = None
            for keyword, genre_name in genre_mapping.items():
                if keyword in title_lower or keyword in description_lower:
                    if genre_name in genre_ids:
                        assigned_genre = genre_name
                        break
            
            # Default to Drama if no specific genre found
            if not assigned_genre:
                assigned_genre = 'Drama'
            
            if assigned_genre in genre_ids:
                assign_genre_to_content(conn, content['id'], genre_ids[assigned_genre])
                print(f"Assigned '{assigned_genre}' to '{content['title']}'")
                fixed_count += 1
            else:
                print(f"Could not assign genre to '{content['title']}' - genre '{assigned_genre}' not found")
        
        print(f"\nFixed {fixed_count} content items with missing genres.")
        
        # Verify the fix
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT c.title, g.name as genre
                FROM content c
                LEFT JOIN content_genres cg ON c.id = cg.content_id
                LEFT JOIN genres g ON cg.genre_id = g.id
                WHERE c.title ILIKE '%christie love%'
                ORDER BY c.title
            """)
            
            christie_love_results = cur.fetchall()
            print(f"\nChristie Love content after fix:")
            for result in christie_love_results:
                print(f"  {result['title']}: {result['genre'] or 'No genre'}")
        
        conn.close()
        print("\nDatabase connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_missing_genres() 