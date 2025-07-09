#!/usr/bin/env python3
"""
Script to update all content poster URLs to use real images from pecantv_title_images folder
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_to_real_title_images():
    """Update all content poster URLs to use real images from GCS"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # GCS base URL for title images
    gcs_base_url = "https://storage.googleapis.com/pecantv_title_images"
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Get all content items
            result = conn.execute(text("""
                SELECT id, title, series_name, type 
                FROM content 
                ORDER BY title
            """))
            
            content_items = result.fetchall()
            updated_count = 0
            
            for item in content_items:
                content_id, title, series_name, content_type = item
                
                # Generate the appropriate poster URL based on title/series
                poster_url = generate_poster_url(title, series_name, content_type, gcs_base_url)
                
                if poster_url:
                    # Update the poster URL
                    conn.execute(text("""
                        UPDATE content 
                        SET poster_url = :poster_url 
                        WHERE id = :content_id
                    """), {
                        "poster_url": poster_url,
                        "content_id": content_id
                    })
                    updated_count += 1
                    print(f"✅ {title}: {poster_url}")
            
            conn.commit()
            print(f"\n🎉 Successfully updated {updated_count} content items with real poster images!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    return True

def generate_poster_url(title, series_name, content_type, gcs_base_url):
    """Generate the appropriate poster URL based on content info"""
    
    # Clean the title for URL generation
    clean_title = title.replace(" ", "-").replace("'", "").replace('"', "").replace("&", "and")
    
    # Handle specific cases based on the database export
    title_mapping = {
        "Petrocelli": "Petrocelli_title-img.jpg",
        "Dragnet": "Dragnet_title-img.png", 
        "Longstreet": "Longstreet_title-img.png",
        "Ghost Squad": "Ghost-Squad_title-img.png",
        "Commando Cody": "CommandoCodyTitleImg-061925.jpg",
        "Lone Ranger": "LoneRanger_TitleImage.png",
        "Green Hornet": "GreenHornet1Title3D-Lite.png",
        "Count of Monte Cristo": "Count-of-Monte-Cristo-sword-fleur-de-lis_title-img.png",
        "Black Brigade": "Black-Brigade-Feature-Img.png",
        "Get Christie Love": "GetChristieLove-Feature-Img-16x9.png",
        "Dementia-13": "dementia-13_Title-Img.png",
        "Carnival of Souls": "Carnival-of-souls_Title-Img.png",
        "Night of the Living Dead": "NLD_title-Img-color.png",
        "Little Shop of Horrors": "Little-Shop-of-Horrors_Title-Img-colorbk.png",
        "The Last Time I Saw Paris": "Last-Time-I-Saw-Paris_Title_Img-1920x1080.jpg",
        "Man with the Golden Arm": "Man-with-the-Golden-Arm-Title-Img.png",
        "Hercules in the Haunted World": "Hercules-in-the-Haunted-World_Title-Img.png",
        "Hercules Against the Moon Men": "Hercules-against-the-Moon-Men_Title-Img.png",
        "Mr. Mean": "MrMean_feature-Img.jpg",
        "Murder in Harlem": "Murder-in-Harlem-Feature-Img.png",
        "Mutiny": "Mutiny_title-img.png",
        "Red House": "Red-House_title-img.png",
        "Scrooge": "Scrooge_title-img.png",
        "Hell in Normandy": "Hell-in-Normandy_title-Img-1920x1080.png",
        "Duel in the Sun": "Duel-in-the-Sun_title-img.png",
        "Dragon Young Master": "Dragon-Young-Master_title-img1.png",
        "Dick Tracy": "Dick-Tracy_Title-Img.jpg",
        "Curse of the Aztec Mummy": "Curse-of-the-Aztec-Mummy_title-img.jpg",
        "Creature": "Creature_title-img.png",
        "Cosmos": "Cosmos-fullLogo_blk.png",
        "Chinese Hercules": "Chinese-Hercules_title-img.png",
        "Captain Scarlett": "Captain-Scarlett_title-img.png",
        "The Chase": "The-Chase_title-img.png",
        "The Flame": "The-Flame_title-img.png",
        "The Master": "The-Master_title-img.png",
        "The Scarlet Pimpernel": "The-Scarlet-Pimpernel_title-img.jpg",
        "The Screaming Skull": "The-Screaming-Skull_title-img.png",
        "Brother from Another Planet": "Brother-from-Another-Planet-Feature-Img.jpg",
        "Bonanza": "Bonanza-Series-Image.jpg",
        "Beyond Christmas": "Beyond-Christmas_title-image.png",
        "Beat the Devil": "Beat-the-Devil_title-img.png",
        "A Christmas Wish": "A-Christmas-Wish_title-image.png",
        "The Adventures of Commando Cody": "CommandoCodyTitleImg-061925.jpg",
        "Passing": "Passing_feature-Img.jpg",
        "The Steel Claw": "The-Steel-Claw_Title-Img-1920x1080.png",
        "The Unholy Four": "The-Unholy-Four_title-img.png",
        "Too Late for Tears": "Too-Late-for-Tears_title-img.png",
        "William Tell": "William-Tell_Title-Img.png",
        "Woman on the Run": "Woman-on-the-Run_title-img.png",
        "Marlowe": "Marlowe_title-img.png",
        "Mike Hammer": "MikeHammer_Title-Img-with-title.png",
        "Man With a Camera": "ManWithACameraSeries_Title-Img-with-title.png",
        "Lying Lips": "Lying-Lips-Feature-Img.png",
        "Charade": "CHARADE-titleImg-Logo.jpg",
        "Lola Colt": "Lola-Colt_title-img.png",
        "Jesse Owens": "Jesse-Owens-Feature-Img.png",
        "Love Affair": "Love-Affair_title-image.png",
        "Scarlett Street": "Scarlet-Street_Title-Img2.jpg",
        "Shockproof": "Shockproof_title-img.png",
        "Silent Night Bloody Night": "Silent-Night-Bloody-Night_title-img-Logo.png",
        "Master of the Flying Guillotine": "Master-of-the-Flying-Guillotine_title-img.png",
        "One Eyed Jacks": "One-Eyed-Jacks_title-img.png",
        "Prisoners of the Lost Planet": "Prisoners-of-the-Lost-Planet_title-img.jpg",
        "Sherlock Holmes - Terror By Night": "Sherlock-Holmes-Series-Img.jpg",
        "Joshua Black Rider": "Joshua-Black-Rider-Feature-Img.png",
        "Jackie Robinson": "Jackie-Robinson_image1.jpg",
        "House on Haunted Hill": "House-on-Haunted-Hill_title-img.png"
    }
    
    # Check if we have a direct mapping
    if title in title_mapping:
        return f"{gcs_base_url}/{title_mapping[title]}"
    
    # For series, try to use series name
    if series_name and series_name in title_mapping:
        return f"{gcs_base_url}/{title_mapping[series_name]}"
    
    # Fallback: try to construct from clean title
    # This is a fallback for any titles not explicitly mapped
    return f"{gcs_base_url}/{clean_title}_title-img.png"

if __name__ == "__main__":
    update_to_real_title_images() 