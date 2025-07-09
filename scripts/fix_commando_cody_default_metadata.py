#!/usr/bin/env python3
"""
Fix Commando Cody episode metadata with default titles and runtime
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

def update_commando_cody_episodes():
    """Update Commando Cody episodes with proper metadata"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get Commando Cody series ID
        cursor.execute("SELECT id FROM content WHERE title ILIKE '%commando cody%'")
        series_result = cursor.fetchone()
        
        if not series_result:
            print("❌ Commando Cody series not found in database")
            return
            
        series_id = series_result[0]
        print(f"✅ Found Commando Cody series ID: {series_id}")
        
        # Default episode titles and descriptions
        episode_data = {
            1: {
                'title': 'Chapter 1: The Space Ship',
                'description': 'Commando Cody and his allies battle against the evil dictator of the planet Ruler and his henchmen in this thrilling space adventure.',
                'runtime': 25
            },
            2: {
                'title': 'Chapter 2: The Atomic Ray',
                'description': 'Commando Cody faces the deadly atomic ray weapon as he continues his mission to protect Earth from the forces of evil.',
                'runtime': 25
            },
            3: {
                'title': 'Chapter 3: The Flying Saucer',
                'description': 'A mysterious flying saucer appears, and Commando Cody must investigate its origins and intentions.',
                'runtime': 25
            },
            4: {
                'title': 'Chapter 4: The Robot Monster',
                'description': 'Commando Cody encounters a terrifying robot monster as he battles to save humanity from destruction.',
                'runtime': 25
            },
            5: {
                'title': 'Chapter 5: The Magnetic Ray',
                'description': 'The enemy unleashes a powerful magnetic ray weapon, and Commando Cody must find a way to counter its effects.',
                'runtime': 25
            },
            6: {
                'title': 'Chapter 6: The Electronic Brain',
                'description': 'Commando Cody discovers an electronic brain controlling the enemy forces and must find a way to disable it.',
                'runtime': 25
            },
            7: {
                'title': 'Chapter 7: The Solar Mirror',
                'description': 'A solar mirror weapon threatens to destroy Earth, and Commando Cody races against time to stop it.',
                'runtime': 25
            },
            8: {
                'title': 'Chapter 8: The Cosmic Ray',
                'description': 'The enemy uses a cosmic ray weapon, and Commando Cody must find a way to protect Earth from its devastating effects.',
                'runtime': 25
            },
            9: {
                'title': 'Chapter 9: The Gravity Ray',
                'description': 'A gravity ray weapon causes chaos on Earth, and Commando Cody must find a way to restore normal conditions.',
                'runtime': 25
            },
            10: {
                'title': 'Chapter 10: The Time Ray',
                'description': 'The enemy threatens to alter time itself, and Commando Cody must prevent this catastrophic event.',
                'runtime': 25
            },
            11: {
                'title': 'Chapter 11: The Mind Ray',
                'description': 'A mind control ray threatens to enslave humanity, and Commando Cody must find a way to break its hold.',
                'runtime': 25
            },
            12: {
                'title': 'Chapter 12: The Final Battle',
                'description': 'Commando Cody faces the ultimate showdown with the forces of evil in this thrilling conclusion.',
                'runtime': 25
            }
        }
        
        updated_count = 0
        
        for episode_num, metadata in episode_data.items():
            # Update the episode
            cursor.execute("""
                UPDATE episodes 
                SET title = %s, 
                    description = %s,
                    runtime = %s
                WHERE series_id = %s AND episode_number = %s
            """, (metadata['title'], metadata['description'], metadata['runtime'], series_id, episode_num))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"✅ Updated Episode {episode_num}: {metadata['title']} ({metadata['runtime']} min)")
            else:
                print(f"❌ No update for Episode {episode_num}")
        
        conn.commit()
        print(f"🎉 Successfully updated {updated_count} episodes")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main function"""
    print("🔧 Fixing Commando Cody episode metadata with default values...")
    update_commando_cody_episodes()
    print("✅ Commando Cody metadata fix complete!")

if __name__ == "__main__":
    main() 