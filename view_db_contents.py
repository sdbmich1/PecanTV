#!/usr/bin/env python3
"""
Simple script to view database contents by ID, title, and type.
"""

import psycopg2

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def view_database_contents():
    """Display all content in the database with ID, title, and type."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Get all content ordered by ID
    cur.execute('SELECT id, title, type FROM content ORDER BY id')
    content = cur.fetchall()
    
    print("DATABASE CONTENTS")
    print("=" * 80)
    print(f"{'ID':<5} {'Type':<10} {'Title'}")
    print("-" * 80)
    
    for row in content:
        content_id, title, content_type = row
        # Truncate long titles for better display
        display_title = title[:60] + "..." if len(title) > 60 else title
        print(f"{content_id:<5} {content_type:<10} {display_title}")
    
    print("-" * 80)
    print(f"Total entries: {len(content)}")
    
    # Show summary by type
    cur.execute('SELECT type, COUNT(*) FROM content GROUP BY type ORDER BY type')
    type_counts = cur.fetchall()
    
    print("\nSUMMARY BY TYPE:")
    print("-" * 30)
    for content_type, count in type_counts:
        print(f"{content_type}: {count}")
    
    conn.close()

if __name__ == "__main__":
    view_database_contents() 