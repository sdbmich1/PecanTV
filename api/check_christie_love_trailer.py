#!/usr/bin/env python3
"""
Check if the remaining 'Get Christie Love' film entry (ID 3) has a trailer_url and print it.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_christie_love_trailer():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, trailer_url FROM content WHERE id=3"))
        row = result.fetchone()
        if not row:
            print("❌ No 'Get Christie Love' film found with ID 3.")
        else:
            print(f"ID: {row[0]}, Title: {row[1]}")
            print(f"  Trailer URL: {row[2]}")
            if row[2]:
                print("✅ Trailer URL exists.")
            else:
                print("❌ No trailer URL found.")

if __name__ == "__main__":
    check_christie_love_trailer() 