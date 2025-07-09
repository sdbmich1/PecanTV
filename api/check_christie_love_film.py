#!/usr/bin/env python3
"""
Check if 'Get Christie Love' is in the database as a FILM and print its content_url if present.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_christie_love_film():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, title, content_url, poster_url
            FROM content
            WHERE LOWER(title) LIKE '%christie love%' OR LOWER(title) LIKE '%get christie love%'
        """))
        films = result.fetchall()
        if not films:
            print("❌ No 'Get Christie Love' film found in the database.")
        else:
            for row in films:
                print(f"ID: {row[0]}, Title: {row[1]}")
                print(f"  Content URL: {row[2]}")
                print(f"  Poster URL: {row[3]}")
                print()

if __name__ == "__main__":
    check_christie_love_film() 