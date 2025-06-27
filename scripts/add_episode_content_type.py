#!/usr/bin/env python3
"""
Script to add 'EPISODE' to the ContentType enum in the Neon database.
"""

import psycopg2

# Database connection parameters for Neon
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def add_episode_content_type():
    """Add EPISODE to the ContentType enum."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Adding EPISODE to ContentType enum")
        print("=" * 50)
        
        # First, check current enum values
        cur.execute("""
            SELECT unnest(enum_range(NULL::content_type)) as enum_value;
        """)
        
        current_values = [row[0] for row in cur.fetchall()]
        print(f"📋 Current ContentType values: {current_values}")
        
        # Check if EPISODE already exists
        if 'EPISODE' in current_values:
            print("✅ EPISODE already exists in ContentType enum")
            return
        
        # Add EPISODE to the enum
        print("➕ Adding EPISODE to ContentType enum...")
        cur.execute("""
            ALTER TYPE content_type ADD VALUE 'EPISODE';
        """)
        conn.commit()  # Commit immediately after ALTER TYPE
        
        # Verify the addition
        cur.execute("""
            SELECT unnest(enum_range(NULL::content_type)) as enum_value;
        """)
        
        new_values = [row[0] for row in cur.fetchall()]
        print(f"📋 Updated ContentType values: {new_values}")
        
        # Check if there are any existing episodes that should be updated
        print("\n🔍 Checking for existing episode content...")
        cur.execute("""
            SELECT id, title, type 
            FROM content 
            WHERE title ILIKE '%episode%' OR title ILIKE '%ep%'
            ORDER BY title;
        """)
        
        episode_content = cur.fetchall()
        if episode_content:
            print("📺 Found content that might be episodes:")
            for content_id, title, content_type in episode_content:
                print(f"   ID {content_id}: {title} (current type: {content_type})")
        else:
            print("📺 No existing episode content found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_episode_content_type() 