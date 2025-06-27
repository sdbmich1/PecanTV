#!/usr/bin/env python3
"""
Create episodes table in Neon database
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neon database connection
NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def create_episodes_table():
    """Create the episodes table in the database."""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS episodes (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        season_number INTEGER NOT NULL,
        episode_number INTEGER NOT NULL,
        runtime INTEGER,
        content_url TEXT NOT NULL,
        poster_url TEXT,
        release_date DATE,
        content_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    add_foreign_key_sql = """
    ALTER TABLE episodes 
    ADD CONSTRAINT fk_episodes_content 
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE;
    """
    
    create_indexes_sql = """
    -- Create unique constraint for season/episode within a series
    CREATE UNIQUE INDEX IF NOT EXISTS unique_episode 
    ON episodes (content_id, season_number, episode_number);
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_episodes_content_id ON episodes(content_id);
    CREATE INDEX IF NOT EXISTS idx_episodes_season_episode ON episodes(season_number, episode_number);
    """
    
    try:
        # Connect to database
        conn = psycopg2.connect(NEON_CONNECTION_STRING)
        cursor = conn.cursor()
        
        print("🔧 Creating episodes table...")
        
        # Execute the SQL in steps
        cursor.execute(create_table_sql)
        print("✅ Table structure created")
        
        try:
            cursor.execute(add_foreign_key_sql)
            print("✅ Foreign key constraint added")
        except Exception as fk_err:
            print(f"⚠️  Foreign key constraint may already exist: {fk_err}")
            conn.rollback()
        
        cursor.execute(create_indexes_sql)
        print("✅ Indexes created")
        
        conn.commit()
        
        print("✅ Episodes table created successfully!")
        
        # Verify the table was created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'episodes'
        """)
        
        if cursor.fetchone():
            print("✅ Table verification successful!")
        else:
            print("❌ Table verification failed!")
            
    except Exception as e:
        print(f"❌ Error creating episodes table: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_episodes_table() 