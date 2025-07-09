#!/usr/bin/env python3
"""
Clear the content_url for The Master directly in the database.
"""
from database import engine
from sqlalchemy import text

def main():
    with engine.connect() as conn:
        result = conn.execute(text("""
            UPDATE content SET content_url = NULL, updated_at = NOW() WHERE title = 'The Master'
        """))
        conn.commit()
        print(f"Rows affected: {result.rowcount}")

if __name__ == "__main__":
    main() 