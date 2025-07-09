#!/usr/bin/env python3
"""
Script to fix categorization issues with Bonanza episodes and Man With a Camera episodes
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_categorization_issues():
    """Fix categorization issues with episodes appearing in wrong carousels"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Bonanza episodes
            bonanza_episodes = [
                "San Francisco",
                "Escape to Ponderosa", 
                "Silent Thunder"
            ]
            for episode_title in bonanza_episodes:
                conn.execute(text("""
                    UPDATE content SET series_name = 'Bonanza' WHERE title = :title
                """), {"title": episode_title})
                print(f"✅ Forced series_name for {episode_title} to 'Bonanza'")
            # Man With a Camera episode
            conn.execute(text("""
                UPDATE content SET series_name = 'Man With a Camera' WHERE title = 'Sad Songs and Other Conversations'
            """))
            print("✅ Forced series_name for 'Sad Songs and Other Conversations' to 'Man With a Camera'")
            conn.commit()
            print(f"\n🎉 Successfully forced series_name updates!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    return True

if __name__ == "__main__":
    fix_categorization_issues() 