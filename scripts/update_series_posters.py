#!/usr/bin/env python3
"""
Update series poster URLs to use better poster images
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

def update_series_posters():
    """Update series poster URLs to use better poster images"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Series poster URL mappings
        series_posters = {
            'Bonanza': '/pecantv_series/dragnet/Dragnet1_poster.jpg',  # Use Dragnet poster as placeholder
            'Ghost Squad': '/pecantv_series/petrocelli/Petrocelli1_poster.jpg',  # Use Petrocelli poster as placeholder
            'Man with a Camera': '/pecantv_series/longstreet/Longstreet1_poster.jpg',  # Use Longstreet poster as placeholder
        }
        
        updated_count = 0
        
        for series_title, poster_url in series_posters.items():
            # Update the series poster URL
            cursor.execute("""
                UPDATE content 
                SET poster_url = %s
                WHERE title = %s
            """, (poster_url, series_title))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated {series_title} poster URL to {poster_url}")
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
    print("🔧 Updating series poster URLs...")
    update_series_posters()
    print("✅ Series poster URL update complete!")

if __name__ == "__main__":
    main() 