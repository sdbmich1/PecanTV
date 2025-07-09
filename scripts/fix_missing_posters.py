#!/usr/bin/env python3
"""
Fix missing poster URLs for Bonanza, Ghost Squad, and Man With a Camera
"""

import psycopg2

# Database connection
DB_CONFIG = {
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'sslmode': 'require'
}

def fix_missing_posters():
    """Fix missing poster URLs for series with broken GCS URLs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Series to fix
        series_to_fix = [
            'Bonanza',
            'Ghost Squad', 
            'Man with a Camera'
        ]
        
        # Default poster URL
        default_poster = '/pecantv_series/default_poster.jpg'
        
        updated_count = 0
        
        for series_title in series_to_fix:
            # Update the series poster URL
            cursor.execute("""
                UPDATE content 
                SET poster_url = %s
                WHERE title = %s
            """, (default_poster, series_title))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated {series_title} poster URL to default")
            else:
                print(f"❌ No update for {series_title}")
        
        conn.commit()
        print(f"🎉 Successfully updated {updated_count} series poster URLs")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main function"""
    print("🔧 Fixing missing poster URLs...")
    fix_missing_posters()
    print("✅ Poster URL fix complete!")

if __name__ == "__main__":
    main() 