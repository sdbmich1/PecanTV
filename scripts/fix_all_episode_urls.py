#!/usr/bin/env python3
import psycopg2

# Neon production database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL)

def fix_longstreet_episodes():
    """Fix Longstreet episode URLs and titles"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Longstreet episode mappings with correct titles and URLs
    longstreet_episodes = [
        (1, "The Way of the Intercepting Fist", "Longstreet-The-Way-of-the-Intercepting-Fist_2p-1080-wCredits.mp4"),
        (2, "A World of Perfect Complicity", "Longstreet-A-World-of-Perfect-Complicity_2p-1080-wCredits.mp4"),
        (3, "The Man Who Killed Himself", "Longstreet-The-Man-Who-Killed-Himself_2p-1080-wCredits.mp4"),
        (4, "So, Who's Fred Hornbeck?", "Longstreet-So-Whos-Fred-Hornbeck_2p-1080-wCredits.mp4"),
        (5, "Elegy in Brass", "Longstreet-Elegy-in-Brass_2p-1080-wCredits.mp4"),
        (6, "Spell Legacy Like Death", "Longstreet-Spell-Legacy-Like-Death_2p-1080-wCredits.mp4"),
        (7, "The Shape of Nightmares", "Longstreet-The-Shape-of-Nightmares_2p-1080-wCredits.mp4"),
        (8, "The Girl with the Broom", "Longstreet-The-Girl-with-the-Broom_2p-1080-wCredits.mp4"),
        (9, "Wednesday's Child", "Longstreet-Wednesdays-Child_2p-1080-wCredits.mp4"),
        (10, "I See', Said the Blind Man", "Longstreet-I-See-Said-the-Blind-Man_2p-1080-wCredits.mp4"),
        (11, "This Little Piggy Went to Marquette", "Longstreet-This-Little-Piggy-Went-to-Marquette_2p-1080-wCredits.mp4"),
        (12, "There Was a Crooked Man", "Longstreet-There-Was-a-Crooked-Man_2p-1080-wCredits.mp4"),
        (13, "The Old Team Spirit", "Longstreet-The-Old-Team-Spirit_2p-1080-wCredits.mp4"),
        (14, "The Long Way Home", "Longstreet-The-Long-Way-Home_2p-1080-wCredits.mp4"),
        (15, "Let the Memories Be Happy Ones", "Longstreet-Let-the-Memories-Be-Happy-Ones_2p-1080-wCredits.mp4"),
        (16, "Survival Times Two", "Longstreet-Survival-Times-Two_2p-1080-wCredits.mp4"),
        (17, "Eye of the Storm", "Longstreet-Eye-of-the-Storm_2p-1080-wCredits.mp4"),
        (18, "Please Leave the Wreck for Others to Enjoy", "Longstreet-Please-Leave-the-Wreck-for-Others-to-Enjoy_2p-1080-wCredits.mp4"),
        (19, "Anatomy of a Mayday", "Longstreet-Anatomy-of-a-Mayday_2p-1080-wCredits.mp4"),
        (20, "Sad Songs and Other Conversations", "Longstreet-Sad-Songs-and-Other-Conversations_2p-1080-wCredits.mp4"),
        (21, "Field of Honor", "Longstreet-Field-of-Honor_2p-1080-wCredits.mp4"),
        (22, "Through Shattering Glass", "Longstreet-Through-Shattering-Glass_2p-1080-wCredits.mp4"),
        (23, "The Long Way Home", "Longstreet-The-Long-Way-Home_2p-1080-wCredits.mp4"),
        (24, "The Girl with the Broom", "Longstreet-The-Girl-with-the-Broom_2p-1080-wCredits.mp4"),
        (25, "Wednesday's Child", "Longstreet-Wednesdays-Child_2p-1080-wCredits.mp4"),
        (26, "I See', Said the Blind Man", "Longstreet-I-See-Said-the-Blind-Man_2p-1080-wCredits.mp4"),
        (27, "This Little Piggy Went to Marquette", "Longstreet-This-Little-Piggy-Went-to-Marquette_2p-1080-wCredits.mp4"),
        (28, "There Was a Crooked Man", "Longstreet-There-Was-a-Crooked-Man_2p-1080-wCredits.mp4"),
        (29, "The Old Team Spirit", "Longstreet-The-Old-Team-Spirit_2p-1080-wCredits.mp4"),
        (30, "The Long Way Home", "Longstreet-The-Long-Way-Home_2p-1080-wCredits.mp4")
    ]
    
    try:
        for episode_num, title, filename in longstreet_episodes:
            content_url = f"https://storage.googleapis.com/pecantv_series/longstreet/{filename}"
            
            cursor.execute("""
                UPDATE episodes 
                SET title = %s, content_url = %s
                WHERE series_id = (SELECT id FROM content WHERE title = 'Longstreet')
                AND episode_number = %s
            """, (title, content_url, episode_num))
            
            print(f"✅ Updated Longstreet Episode {episode_num}: {title}")
        
        conn.commit()
        print(f"✅ Updated {len(longstreet_episodes)} Longstreet episodes")
        
    except Exception as e:
        print(f"❌ Error updating Longstreet episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def fix_ghost_squad_episodes():
    """Fix Ghost Squad episode URLs"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Ghost Squad episode mappings
    ghost_squad_episodes = [
        (1, "The Heir Apparent", "GS-The-Heir-Apparent_1080-wCredits.mp4"),
        (2, "The Death Game", "GS-The-Death-Game_1080-wCredits.mp4"),
        (3, "The Man Who Wouldn't Die", "GS-The-Man-Who-Wouldnt-Die_1080-wCredits.mp4"),
        (4, "The Deadly Masquerade", "GS-The-Deadly-Masquerade_1080-wCredits.mp4"),
        (5, "The Silent Killers", "GS-The-Silent-Killers_1080-wCredits.mp4")
    ]
    
    try:
        for episode_num, title, filename in ghost_squad_episodes:
            content_url = f"https://storage.googleapis.com/pecantv_series/ghost_squad/{filename}"
            
            cursor.execute("""
                UPDATE episodes 
                SET title = %s, content_url = %s
                WHERE series_id = (SELECT id FROM content WHERE title = 'Ghost Squad')
                AND episode_number = %s
            """, (title, content_url, episode_num))
            
            print(f"✅ Updated Ghost Squad Episode {episode_num}: {title}")
        
        conn.commit()
        print(f"✅ Updated {len(ghost_squad_episodes)} Ghost Squad episodes")
        
    except Exception as e:
        print(f"❌ Error updating Ghost Squad episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def fix_mike_hammer_episodes():
    """Fix Mike Hammer episode URLs"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Mike Hammer episode mappings
    mike_hammer_episodes = [
        (1, "The New York Rock", "MH-The-New-York-Rock_1080-wCredits.mp4"),
        (2, "The Long Wait", "MH-The-Long-Wait_1080-wCredits.mp4"),
        (3, "The High Cost of Dying", "MH-The-High-Cost-of-Dying_1080-wCredits.mp4"),
        (4, "The Girl in the Red Bikini", "MH-The-Girl-in-the-Red-Bikini_1080-wCredits.mp4")
    ]
    
    try:
        for episode_num, title, filename in mike_hammer_episodes:
            content_url = f"https://storage.googleapis.com/pecantv_series/mike_hammer/{filename}"
            
            cursor.execute("""
                UPDATE episodes 
                SET title = %s, content_url = %s
                WHERE series_id = (SELECT id FROM content WHERE title = 'Mike Hammer')
                AND episode_number = %s
            """, (title, content_url, episode_num))
            
            print(f"✅ Updated Mike Hammer Episode {episode_num}: {title}")
        
        conn.commit()
        print(f"✅ Updated {len(mike_hammer_episodes)} Mike Hammer episodes")
        
    except Exception as e:
        print(f"❌ Error updating Mike Hammer episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def fix_bonanza_episodes():
    """Fix Bonanza episode URLs and titles"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Bonanza episode mappings with correct titles and URLs
    bonanza_episodes = [
        (1, "A Rose for Lotta", "Bonanza-A-Rose-for-Lotta_2p-1080-wCredits.mp4"),
        (2, "Death on Sun Mountain", "Bonanza-Death-on-Sun-Mountain_2p-1080-wCredits.mp4"),
        (3, "The Newcomers", "Bonanza-The-Newcomers_2p-1080-wCredits.mp4"),
        (4, "The Paiute War", "Bonanza-The-Paiute-War_2p-1080-wCredits.mp4"),
        (5, "Enter Mark Twain", "Bonanza-Enter-Mark-Twain_2p-1080-wCredits.mp4"),
        (6, "The Julia Bulette Story", "Bonanza-The-Julia-Bulette-Story_2p-1080-wCredits.mp4"),
        (7, "The Saga of Annie O'Toole", "Bonanza-The-Saga-of-Annie-OToole_2p-1080-wCredits.mp4"),
        (8, "The Philip Deidesheimer Story", "Bonanza-The-Philip-Deidesheimer-Story_2p-1080-wCredits.mp4"),
        (9, "Mr. Henry Comstock", "Bonanza-Mr-Henry-Comstock_2p-1080-wCredits.mp4"),
        (10, "The Magnificent Adah", "Bonanza-The-Magnificent-Adah_2p-1080-wCredits.mp4"),
        (11, "The Truckee Strip", "Bonanza-The-Truckee-Strip_2p-1080-wCredits.mp4"),
        (12, "The Hanging Posse", "Bonanza-The-Hanging-Posse_2p-1080-wCredits.mp4"),
        (13, "The Spanish Grant", "Bonanza-The-Spanish-Grant_2p-1080-wCredits.mp4")
    ]
    
    try:
        for episode_num, title, filename in bonanza_episodes:
            content_url = f"https://storage.googleapis.com/pecantv_series/bonanza/{filename}"
            
            cursor.execute("""
                UPDATE episodes 
                SET title = %s, content_url = %s
                WHERE series_id = (SELECT id FROM content WHERE title = 'Bonanza')
                AND episode_number = %s
            """, (title, content_url, episode_num))
            
            print(f"✅ Updated Bonanza Episode {episode_num}: {title}")
        
        conn.commit()
        print(f"✅ Updated {len(bonanza_episodes)} Bonanza episodes")
        
    except Exception as e:
        print(f"❌ Error updating Bonanza episodes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    print("🔧 Fixing all episode URLs and titles...")
    
    print("\n📺 Fixing Longstreet episodes...")
    fix_longstreet_episodes()
    
    print("\n👻 Fixing Ghost Squad episodes...")
    fix_ghost_squad_episodes()
    
    print("\n🔨 Fixing Mike Hammer episodes...")
    fix_mike_hammer_episodes()
    
    print("\n🐎 Fixing Bonanza episodes...")
    fix_bonanza_episodes()
    
    print("\n✅ All episode fixes completed!")

if __name__ == "__main__":
    main() 