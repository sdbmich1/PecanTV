#!/usr/bin/env python3
"""
Remove the duplicate 'Get Christie Love!' film entry with ID 518 from the database.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def remove_duplicate_christie_love():
    with engine.connect() as conn:
        # Check if the entry exists
        result = conn.execute(text("SELECT id, title FROM content WHERE id=518"))
        row = result.fetchone()
        if not row:
            print("No duplicate found with ID 518.")
            return
        print(f"Deleting duplicate: ID {row[0]}, Title: {row[1]}")
        conn.execute(text("DELETE FROM content WHERE id=518"))
        conn.commit()
        print("✅ Duplicate removed.")

if __name__ == "__main__":
    remove_duplicate_christie_love() 