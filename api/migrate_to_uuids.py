#!/usr/bin/env python3
"""
Migrate PecanTV database from integer IDs to UUIDs for global solution
This script will:
1. Add UUID columns to all tables
2. Generate UUIDs for existing data
3. Update foreign key relationships
4. Drop old integer columns
"""

import psycopg2
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neon database connection
NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def migrate_to_uuids():
    """Migrate all tables from integer IDs to UUIDs."""
    
    try:
        # Connect to database
        conn = psycopg2.connect(NEON_CONNECTION_STRING)
        cursor = conn.cursor()
        
        print("🚀 Starting UUID migration...")
        
        # Step 1: Add UUID columns
        print("📋 Step 1: Adding UUID columns...")
        
        # Add uuid columns to all relevant tables
        cursor.execute("""
            ALTER TABLE content ADD COLUMN IF NOT EXISTS uuid UUID;
            ALTER TABLE genres ADD COLUMN IF NOT EXISTS uuid UUID;
            ALTER TABLE ratings ADD COLUMN IF NOT EXISTS uuid UUID;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS uuid UUID;
            ALTER TABLE episodes ADD COLUMN IF NOT EXISTS uuid UUID;
        """)
        
        print("✅ UUID columns added")
        
        # Step 2: Generate UUIDs for existing data
        print("🔄 Step 2: Generating UUIDs for existing data...")
        
        # Update tables with UUIDs
        cursor.execute("""
            UPDATE content SET uuid = gen_random_uuid() WHERE uuid IS NULL;
        """)
        cursor.execute("""
            UPDATE genres SET uuid = gen_random_uuid() WHERE uuid IS NULL;
        """)
        cursor.execute("""
            UPDATE ratings SET uuid = gen_random_uuid() WHERE uuid IS NULL;
        """)
        cursor.execute("""
            UPDATE users SET uuid = gen_random_uuid() WHERE uuid IS NULL;
        """)
        cursor.execute("""
            UPDATE episodes SET uuid = gen_random_uuid() WHERE uuid IS NULL;
        """)
        
        print("✅ UUIDs generated for existing data")
        
        # Step 3: Create new indexes and constraints
        print("🔗 Step 3: Creating new indexes and constraints...")
        
        # Make UUID columns NOT NULL
        cursor.execute("""
            ALTER TABLE content ALTER COLUMN uuid SET NOT NULL;
            ALTER TABLE genres ALTER COLUMN uuid SET NOT NULL;
            ALTER TABLE ratings ALTER COLUMN uuid SET NOT NULL;
            ALTER TABLE users ALTER COLUMN uuid SET NOT NULL;
            ALTER TABLE episodes ALTER COLUMN uuid SET NOT NULL;
        """)
        
        # Create unique indexes on UUID columns
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_content_uuid ON content(uuid);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_genres_uuid ON genres(uuid);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_ratings_uuid ON ratings(uuid);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_uuid ON users(uuid);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_episodes_uuid ON episodes(uuid);
        """)
        
        # Create foreign key constraint for episodes
        cursor.execute("""
            ALTER TABLE episodes 
            ADD COLUMN IF NOT EXISTS content_uuid UUID;
        """)
        cursor.execute("""
            UPDATE episodes SET content_uuid = c.uuid FROM content c WHERE episodes.series_id = c.id;
        """)
        cursor.execute("""
            ALTER TABLE episodes ALTER COLUMN content_uuid SET NOT NULL;
        """)
        cursor.execute("""
            ALTER TABLE episodes 
            ADD CONSTRAINT fk_episodes_content_uuid 
            FOREIGN KEY (content_uuid) REFERENCES content(uuid) ON DELETE CASCADE;
        """)
        
        # Create unique constraint for episodes
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_episode_uuid 
            ON episodes (content_uuid, season_number, episode_number);
        """)
        
        print("✅ New indexes and constraints created")
        
        # Step 4: Update content_genres junction table
        print("🔗 Step 4: Updating junction tables...")
        
        # Add UUID columns to content_genres
        cursor.execute("""
            ALTER TABLE content_genres ADD COLUMN IF NOT EXISTS content_uuid UUID;
            ALTER TABLE content_genres ADD COLUMN IF NOT EXISTS genre_uuid UUID;
        """)
        
        # Update content_genres with UUID references
        cursor.execute("""
            UPDATE content_genres 
            SET content_uuid = c.uuid, genre_uuid = g.uuid
            FROM content c, genres g
            WHERE content_genres.content_id = c.id 
            AND content_genres.genre_id = g.id;
        """)
        
        # Make UUID columns NOT NULL
        cursor.execute("""
            ALTER TABLE content_genres ALTER COLUMN content_uuid SET NOT NULL;
            ALTER TABLE content_genres ALTER COLUMN genre_uuid SET NOT NULL;
        """)
        
        # Add foreign key constraints
        cursor.execute("""
            ALTER TABLE content_genres 
            ADD CONSTRAINT fk_content_genres_content_uuid 
            FOREIGN KEY (content_uuid) REFERENCES content(uuid) ON DELETE CASCADE;
            
            ALTER TABLE content_genres 
            ADD CONSTRAINT fk_content_genres_genre_uuid 
            FOREIGN KEY (genre_uuid) REFERENCES genres(uuid) ON DELETE CASCADE;
        """)
        
        print("✅ Junction tables updated")
        
        # Commit all changes
        conn.commit()
        
        print("🎉 UUID migration completed successfully!")
        
        # Verify the migration
        print("🔍 Verifying migration...")
        
        cursor.execute("SELECT COUNT(*) FROM content WHERE uuid IS NOT NULL")
        content_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM genres WHERE uuid IS NOT NULL")
        genres_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE uuid IS NOT NULL")
        ratings_count = cursor.fetchone()[0]
        
        print(f"✅ Content records with UUIDs: {content_count}")
        print(f"✅ Genre records with UUIDs: {genres_count}")
        print(f"✅ Rating records with UUIDs: {ratings_count}")
        
        # Show sample UUIDs
        cursor.execute("SELECT title, uuid FROM content LIMIT 3")
        samples = cursor.fetchall()
        print("📺 Sample content UUIDs:")
        for title, uuid in samples:
            print(f"   - {title}: {uuid}")
            
    except Exception as e:
        print(f"❌ Error during UUID migration: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def cleanup_old_columns():
    """Remove old integer ID columns after confirming UUID migration works."""
    
    try:
        conn = psycopg2.connect(NEON_CONNECTION_STRING)
        cursor = conn.cursor()
        
        print("🧹 Cleaning up old integer columns...")
        
        # Drop old foreign key constraints first
        cursor.execute("""
            ALTER TABLE content_genres DROP CONSTRAINT IF EXISTS fk_content_genres_content;
            ALTER TABLE content_genres DROP CONSTRAINT IF EXISTS fk_content_genres_genre;
        """)
        
        # Drop old columns
        cursor.execute("""
            ALTER TABLE content_genres DROP COLUMN IF EXISTS content_id;
            ALTER TABLE content_genres DROP COLUMN IF EXISTS genre_id;
            ALTER TABLE content_genres DROP COLUMN IF EXISTS id;
        """)
        
        # Drop old indexes
        cursor.execute("""
            DROP INDEX IF EXISTS idx_content_genres_content_id;
            DROP INDEX IF EXISTS idx_content_genres_genre_id;
        """)
        
        conn.commit()
        print("✅ Old columns cleaned up")
        
    except Exception as e:
        print(f"❌ Error cleaning up old columns: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 PecanTV UUID Migration Tool")
    print("==============================")
    cleanup_old_columns() 