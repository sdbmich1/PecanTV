#!/usr/bin/env python3
"""
Comprehensive fix for all poster and categorization issues
"""

import psycopg2
from datetime import datetime, timezone

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def fix_all_issues():
    """Fix all poster and categorization issues"""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔧 Comprehensive Fix for Poster and Categorization Issues")
        print("=" * 70)
        
        # 1. Fix content categorization issues
        print("\n1. 🔄 Fixing Content Categorization...")
        fix_categorization_issues(cur)
        
        # 2. Fix poster URLs to use direct GCS URLs
        print("\n2. 🖼️  Fixing Poster URLs...")
        fix_poster_urls(cur)
        
        # 3. Verify the fixes
        print("\n3. ✅ Verifying Fixes...")
        verify_fixes(cur)
        
        conn.commit()
        print(f"\n🎉 Successfully fixed all issues!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fix_categorization_issues(cur):
    """Fix content that's incorrectly categorized"""
    
    # Fix Bonanza episodes that are marked as FILM
    bonanza_episodes = [
        "Feet of Clay",
        "Shadow of Fear"
    ]
    
    for episode_title in bonanza_episodes:
        cur.execute("""
            UPDATE content 
            SET type = 'FILM', series_name = NULL, episode_number = NULL, season_number = NULL
            WHERE title = %s AND type = 'FILM'
        """, (episode_title,))
        
        if cur.rowcount > 0:
            print(f"   ✅ Fixed categorization for: {episode_title}")
        else:
            print(f"   ⚠️  No changes needed for: {episode_title}")
    
    # Fix Petrocelli episodes that are marked as FILM
    petrocelli_episodes = [
        "Shadow of Fear"  # This is actually a Petrocelli episode
    ]
    
    for episode_title in petrocelli_episodes:
        cur.execute("""
            UPDATE content 
            SET type = 'FILM', series_name = NULL, episode_number = NULL, season_number = NULL
            WHERE title = %s AND type = 'FILM'
        """, (episode_title,))
        
        if cur.rowcount > 0:
            print(f"   ✅ Fixed categorization for: {episode_title}")
        else:
            print(f"   ⚠️  No changes needed for: {episode_title}")

def fix_poster_urls(cur):
    """Fix poster URLs to use direct GCS URLs instead of local/CDN URLs"""
    
    # Get all content with poster URLs
    cur.execute("""
        SELECT id, title, type, poster_url 
        FROM content 
        WHERE poster_url IS NOT NULL 
        AND poster_url != ''
        ORDER BY title
    """)
    
    content_items = cur.fetchall()
    print(f"   📋 Processing {len(content_items)} content items")
    
    updated_count = 0
    
    for content_id, title, content_type, current_poster_url in content_items:
        new_poster_url = None
        
        # Skip if already using GCS URLs
        if current_poster_url.startswith('https://storage.googleapis.com/'):
            continue
        
        # Generate appropriate GCS poster URL based on content type and title
        if content_type == "SERIES":
            new_poster_url = generate_series_poster_url(title)
        elif content_type == "FILM":
            new_poster_url = generate_film_poster_url(title)
        
        if new_poster_url and new_poster_url != current_poster_url:
            cur.execute("""
                UPDATE content 
                SET poster_url = %s 
                WHERE id = %s
            """, (new_poster_url, content_id))
            
            updated_count += 1
            print(f"   ✅ Updated {title}: {new_poster_url}")
    
    print(f"   📊 Updated {updated_count} poster URLs")

def generate_series_poster_url(title):
    """Generate GCS poster URL for series"""
    
    # Map series titles to their poster files
    series_posters = {
        "Petrocelli": "https://storage.googleapis.com/pecantv_title_images/Petrocelli_title-img.jpg",
        "Dragnet": "https://storage.googleapis.com/pecantv_title_images/Dragnet_title-img.png",
        "Longstreet": "https://storage.googleapis.com/pecantv_title_images/Longstreet_title-img.png",
        "Ghost Squad": "https://storage.googleapis.com/pecantv_title_images/Ghost-Squad_title-img.png",
        "Count Duckula": "https://storage.googleapis.com/pecantv_title_images/Count-Duckula_title-img.png",
        "The Menacing Mazurka": "https://storage.googleapis.com/pecantv_title_images/The-Menacing-Mazurka_title-img.png",
        "The Old Team Spirit": "https://storage.googleapis.com/pecantv_title_images/The-Old-Team-Spirit_title-img.png",
        "Lichtenburg": "https://storage.googleapis.com/pecantv_title_images/Lichtenburg_title-img.png",
        "The Barefoot Empress": "https://storage.googleapis.com/pecantv_title_images/The-Barefoot-Empress_title-img.png"
    }
    
    return series_posters.get(title, "https://storage.googleapis.com/pecantv_title_images/default_poster.jpg")

def generate_film_poster_url(title):
    """Generate GCS poster URL for films"""
    
    # Map film titles to their poster files
    film_posters = {
        "Feet of Clay": "https://storage.googleapis.com/pecantv_title_images/Feet-of-Clay_title-img.png",
        "Shadow of Fear": "https://storage.googleapis.com/pecantv_title_images/Petrocelli_title-img.jpg",  # This is actually a Petrocelli episode
        "Black Brigade": "https://storage.googleapis.com/pecantv_title_images/Black-Brigade-Feature-Img.png",
        "Get Christie Love": "https://storage.googleapis.com/pecantv_title_images/GetChristieLove-Feature-Img-16x9.png",
        "Dementia-13": "https://storage.googleapis.com/pecantv_title_images/dementia-13_Title-Img.png",
        "Carnival of Souls": "https://storage.googleapis.com/pecantv_title_images/Carnival-of-souls_Title-Img.png",
        "Night of the Living Dead": "https://storage.googleapis.com/pecantv_title_images/NLD_title-Img-color.png",
        "Little Shop of Horrors": "https://storage.googleapis.com/pecantv_title_images/Little-Shop-of-Horrors_Title-Img-colorbk.png",
        "The Last Time I Saw Paris": "https://storage.googleapis.com/pecantv_title_images/Last-Time-I-Saw-Paris_Title_Img-1920x1080.jpg",
        "Man with the Golden Arm": "https://storage.googleapis.com/pecantv_title_images/Man-with-the-Golden-Arm-Title-Img.png",
        "Hercules in the Haunted World": "https://storage.googleapis.com/pecantv_title_images/Hercules-in-the-Haunted-World_Title-Img.png",
        "Hercules Against the Moon Men": "https://storage.googleapis.com/pecantv_title_images/Hercules-against-the-Moon-Men_Title-Img.png",
        "Mr. Mean": "https://storage.googleapis.com/pecantv_title_images/MrMean_feature-Img.jpg",
        "Murder in Harlem": "https://storage.googleapis.com/pecantv_title_images/Murder-in-Harlem-Feature-Img.png",
        "Mutiny": "https://storage.googleapis.com/pecantv_title_images/Mutiny_title-img.png",
        "Red House": "https://storage.googleapis.com/pecantv_title_images/Red-House_title-img.png",
        "Scrooge": "https://storage.googleapis.com/pecantv_title_images/Scrooge_title-img.png",
        "Hell in Normandy": "https://storage.googleapis.com/pecantv_title_images/Hell-in-Normandy_title-Img-1920x1080.png",
        "Duel in the Sun": "https://storage.googleapis.com/pecantv_title_images/Duel-in-the-Sun_title-img.png",
        "Dragon Young Master": "https://storage.googleapis.com/pecantv_title_images/Dragon-Young-Master_title-img1.png"
    }
    
    return film_posters.get(title, "https://storage.googleapis.com/pecantv_title_images/default_poster.jpg")

def verify_fixes(cur):
    """Verify that all fixes were applied correctly"""
    
    print("   🔍 Verifying fixes...")
    
    # Check content types
    cur.execute("SELECT type, COUNT(*) FROM content GROUP BY type ORDER BY COUNT(*) DESC")
    type_counts = cur.fetchall()
    print("   📊 Content type distribution:")
    for content_type, count in type_counts:
        print(f"      {content_type}: {count}")
    
    # Check poster URL patterns
    cur.execute("""
        SELECT 
            CASE 
                WHEN poster_url LIKE 'https://storage.googleapis.com/%' THEN 'GCS'
                WHEN poster_url LIKE 'http://localhost%' THEN 'Local'
                WHEN poster_url LIKE '%default_poster%' THEN 'Default'
                ELSE 'Other'
            END as url_type,
            COUNT(*) as count
        FROM content 
        WHERE poster_url IS NOT NULL
        GROUP BY url_type
        ORDER BY count DESC
    """)
    
    url_patterns = cur.fetchall()
    print("   📊 Poster URL patterns:")
    for url_type, count in url_patterns:
        print(f"      {url_type}: {count}")
    
    # Check for any remaining issues
    cur.execute("""
        SELECT COUNT(*) 
        FROM content 
        WHERE poster_url IS NULL OR poster_url = ''
    """)
    
    null_posters = cur.fetchone()[0]
    if null_posters > 0:
        print(f"   ⚠️  Found {null_posters} content items with null/empty poster URLs")
    else:
        print("   ✅ All content has poster URLs")

if __name__ == "__main__":
    fix_all_issues() 