#!/usr/bin/env python3
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("UPDATE content SET content_url = NULL, updated_at = NOW() WHERE title = 'The Master'"))
    conn.commit()
    print(f"Rows affected: {result.rowcount}") 