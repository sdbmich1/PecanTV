#!/usr/bin/env python3
"""
Fix poster URLs for Count Duckula and Inframan
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

def fix_count_duckula_inframan_posters():
    """Fix poster URLs for Count Duckula and Inframan"""
    print("🔧 Fixing poster URLs for Count Duckula and Inframan")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        # 1. Fix Count Duckula poster URL
        print("📺 1. Fixing Count Duckula poster URL...")
        count_duckula_poster = "https://storage.googleapis.com/pecantv_title_images/Count-Duckula-poster1080.jpg"
        
        cur.execute("""
            UPDATE content 
            SET poster_url = %s
            WHERE id = 82 AND title = 'Count Duckula'
        """, (count_duckula_poster,))
        
        if cur.rowcount > 0:
            print(f"✅ Updated Count Duckula poster URL to: {count_duckula_poster}")
        else:
            print("❌ Count Duckula not found or not updated")
        
        # 2. Fix Inframan poster URL
        print("\n📺 2. Fixing Inframan poster URL...")
        inframan_poster = "https://storage.googleapis.com/pecantv_title_images/Inframan_title-img.png"
        
        cur.execute("""
            UPDATE content 
            SET poster_url = %s
            WHERE id = 84 AND title = 'Inframan'
        """, (inframan_poster,))
        
        if cur.rowcount > 0:
            print(f"✅ Updated Inframan poster URL to: {inframan_poster}")
        else:
            print("❌ Inframan not found or not updated")
        
        # 3. Check if Inframan should be filtered out (if no poster exists)
        print("\n🔍 3. Checking if Inframan poster exists...")
        import requests
        try:
            response = requests.head(inframan_poster, timeout=5)
            if response.status_code == 200:
                print("✅ Inframan poster exists and is accessible")
            else:
                print(f"❌ Inframan poster not accessible (status: {response.status_code})")
                print("   Consider removing Inframan from carousel or adding a poster")
        except Exception as e:
            print(f"❌ Error checking Inframan poster: {e}")
            print("   Consider removing Inframan from carousel or adding a poster")
        
        conn.commit()
        print(f"\n✅ Poster updates completed!")
        
        # 4. Verify the changes
        print("\n🔍 4. Verifying changes...")
        cur.execute("""
            SELECT id, title, poster_url 
            FROM content 
            WHERE id IN (82, 84)
            ORDER BY id
        """)
        
        results = cur.fetchall()
        for content_id, title, poster_url in results:
            print(f"  {title} (ID: {content_id}): {poster_url or 'NO POSTER'}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_count_duckula_inframan_posters() 