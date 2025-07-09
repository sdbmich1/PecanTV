#!/usr/bin/env python3
"""
Find the correct Bonanza series ID
"""

import os
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def main():
    print("🔍 Finding Bonanza series ID...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all series IDs
        result = conn.execute(text("""
            SELECT DISTINCT series_id FROM episodes ORDER BY series_id
        """))
        
        series_ids = [row[0] for row in result.fetchall()]
        print(f"Found series IDs: {series_ids}")
        
        # Check each series for Bonanza episodes
        for series_id in series_ids:
            result = conn.execute(text("""
                SELECT title FROM episodes WHERE series_id = :series_id LIMIT 5
            """), {'series_id': series_id})
            
            titles = [row[0] for row in result.fetchall()]
            print(f"\nSeries {series_id}: {titles}")
            
            # Check if any titles contain Bonanza-related keywords
            bonanza_keywords = ['bonanza', 'cartwright', 'ponderosa', 'savage', 'reckoning']
            for title in titles:
                if any(keyword in title.lower() for keyword in bonanza_keywords):
                    print(f"   🎯 Potential Bonanza series found: {series_id}")
                    break

if __name__ == "__main__":
    main() 