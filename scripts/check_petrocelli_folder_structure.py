#!/usr/bin/env python3
"""
Script to check the petrocelli_final_episodes folder structure and find all files.
"""

import requests
import time

# Base URL for Petrocelli files in GCS
BASE_URL = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

def test_file_exists(filename):
    """Test if a file exists in GCS."""
    url = BASE_URL + filename
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def check_petrocelli_folder():
    """Check the petrocelli_final_episodes folder for all possible files."""
    print("🔍 Checking petrocelli_final_episodes folder structure...")
    print("=" * 70)
    
    # Test for files that might have completely different naming patterns
    test_patterns = [
        # Simple numbered files
        "1.mp4", "2.mp4", "3.mp4", "4.mp4", "5.mp4", "6.mp4", "7.mp4", "8.mp4", "9.mp4", "10.mp4",
        "11.mp4", "12.mp4", "13.mp4", "14.mp4", "15.mp4", "16.mp4", "17.mp4", "18.mp4", "19.mp4", "20.mp4", "21.mp4", "22.mp4",
        
        # Episode numbered files
        "Episode1.mp4", "Episode2.mp4", "Episode3.mp4", "Episode4.mp4", "Episode5.mp4", "Episode6.mp4", "Episode7.mp4", "Episode8.mp4", "Episode9.mp4", "Episode10.mp4",
        "Episode11.mp4", "Episode12.mp4", "Episode13.mp4", "Episode14.mp4", "Episode15.mp4", "Episode16.mp4", "Episode17.mp4", "Episode18.mp4", "Episode19.mp4", "Episode20.mp4", "Episode21.mp4", "Episode22.mp4",
        
        # Different naming patterns
        "Petrocelli_1.mp4", "Petrocelli_2.mp4", "Petrocelli_3.mp4", "Petrocelli_4.mp4", "Petrocelli_5.mp4", "Petrocelli_6.mp4", "Petrocelli_7.mp4", "Petrocelli_8.mp4", "Petrocelli_9.mp4", "Petrocelli_10.mp4",
        "Petrocelli_11.mp4", "Petrocelli_12.mp4", "Petrocelli_13.mp4", "Petrocelli_14.mp4", "Petrocelli_15.mp4", "Petrocelli_16.mp4", "Petrocelli_17.mp4", "Petrocelli_18.mp4", "Petrocelli_19.mp4", "Petrocelli_20.mp4", "Petrocelli_21.mp4", "Petrocelli_22.mp4",
        
        # With different extensions
        "Petrocelli1.m4v", "Petrocelli2.m4v", "Petrocelli3.m4v", "Petrocelli4.m4v", "Petrocelli5.m4v", "Petrocelli6.m4v", "Petrocelli7.m4v", "Petrocelli8.m4v", "Petrocelli9.m4v", "Petrocelli10.m4v",
        "Petrocelli11.m4v", "Petrocelli12.m4v", "Petrocelli13.m4v", "Petrocelli14.m4v", "Petrocelli15.m4v", "Petrocelli16.m4v", "Petrocelli17.m4v", "Petrocelli18.m4v", "Petrocelli19.m4v", "Petrocelli20.m4v", "Petrocelli21.m4v", "Petrocelli22.m4v",
        
        # Different quality patterns
        "Petrocelli1_HD.mp4", "Petrocelli2_HD.mp4", "Petrocelli3_HD.mp4", "Petrocelli4_HD.mp4", "Petrocelli5_HD.mp4", "Petrocelli6_HD.mp4", "Petrocelli7_HD.mp4", "Petrocelli8_HD.mp4", "Petrocelli9_HD.mp4", "Petrocelli10_HD.mp4",
        "Petrocelli11_HD.mp4", "Petrocelli12_HD.mp4", "Petrocelli13_HD.mp4", "Petrocelli14_HD.mp4", "Petrocelli15_HD.mp4", "Petrocelli16_HD.mp4", "Petrocelli17_HD.mp4", "Petrocelli18_HD.mp4", "Petrocelli19_HD.mp4", "Petrocelli20_HD.mp4", "Petrocelli21_HD.mp4", "Petrocelli22_HD.mp4",
        
        # Check for files without "Petrocelli" prefix
        "Episode1_2p-1080-wCredits.mp4", "Episode2_2p-1080-wCredits.mp4", "Episode3_2p-1080-wCredits.mp4", "Episode4_2p-1080-wCredits.mp4", "Episode5_2p-1080-wCredits.mp4", "Episode6_2p-1080-wCredits.mp4", "Episode7_2p-1080-wCredits.mp4", "Episode8_2p-1080-wCredits.mp4", "Episode9_2p-1080-wCredits.mp4", "Episode10_2p-1080-wCredits.mp4",
        "Episode11_2p-1080-wCredits.mp4", "Episode12_2p-1080-wCredits.mp4", "Episode13_2p-1080-wCredits.mp4", "Episode14_2p-1080-wCredits.mp4", "Episode15_2p-1080-wCredits.mp4", "Episode16_2p-1080-wCredits.mp4", "Episode17_2p-1080-wCredits.mp4", "Episode18_2p-1080-wCredits.mp4", "Episode19_2p-1080-wCredits.mp4", "Episode20_2p-1080-wCredits.mp4", "Episode21_2p-1080-wCredits.mp4", "Episode22_2p-1080-wCredits.mp4",
        
        # Check for files with just episode titles
        "Deadly-Journey_2p-1080-wCredits.mp4", "Face-of-Evil_2p-1080-wCredits.mp4", "Four-the-Hard-Way_2p-1080-wCredits.mp4", "Shadow-of-Fear_2p-1080-wCredits.mp4", "The-Night-Visitor_2p-1080-wCredits.mp4", "Too-Many-Alibis_2p-1080-wCredits.mp4", "Shadow-of-a-Doubt_2p-1080-wCredits.mp4", "Survival_2p-1080-wCredits.mp4", "Death-in-Small-Doses_2p-1080-wCredits.mp4",
        "Once-Upon-A-Victim_2p-1080-wCredits.mp4", "A-Deadly-Game_2p-1080-wCredits.mp4", "The-Deadly-Trap_2p-1080-wCredits.mp4", "The-Deadly-Double_2p-1080-wCredits.mp4", "A-Deadly-Charade_2p-1080-wCredits.mp4", "The-Deadly-Connection_2p-1080-wCredits.mp4", "Death-of-a-Friend_2p-1080-wCredits.mp4", "The-Deadly-Truth_2p-1080-wCredits.mp4", "A-Deadly-Secret_2p-1080-wCredits.mp4", "The-Deadly-Web_2p-1080-wCredits.mp4", "Death-by-Design_2p-1080-wCredits.mp4", "The-Deadly-Plan_2p-1080-wCredits.mp4", "The-Deadly-Contract_2p-1080-wCredits.mp4"
    ]
    
    existing_files = []
    
    print(f"Testing {len(test_patterns)} different naming patterns...")
    print("=" * 50)
    
    for i, filename in enumerate(test_patterns, 1):
        if test_file_exists(filename):
            existing_files.append(filename)
            print(f"✅ {i:3d}. {filename}")
        else:
            print(f"❌ {i:3d}. {filename}")
        
        # Add a small delay to avoid overwhelming the server
        if i % 20 == 0:
            time.sleep(0.2)
    
    print(f"\n📊 SUMMARY:")
    print("=" * 40)
    print(f"Total patterns tested: {len(test_patterns)}")
    print(f"Files that exist: {len(existing_files)}")
    print(f"Files missing: {len(test_patterns) - len(existing_files)}")
    
    if existing_files:
        print(f"\n✅ EXISTING FILES:")
        for i, filename in enumerate(existing_files, 1):
            print(f"  {i:2d}. {filename}")
    
    return existing_files

if __name__ == "__main__":
    existing_files = check_petrocelli_folder()
    print(f"\n🎯 Found {len(existing_files)} files with alternative naming patterns") 