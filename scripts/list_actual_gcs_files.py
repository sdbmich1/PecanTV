#!/usr/bin/env python3
"""
Script to list ALL actual files in the GCS petrocelli_final_episodes folder.
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

def list_all_actual_files():
    """List ALL actual files in the GCS petrocelli_final_episodes folder."""
    print("🔍 Listing ALL actual files in GCS petrocelli_final_episodes folder...")
    print("=" * 70)
    
    # Comprehensive list of ALL possible Petrocelli episode filenames
    all_possible_files = [
        # Episode 1
        "Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4",
        "Petrocelli1.mp4",
        "Petrocelli-Episode-1.mp4",
        "Petrocelli-Episode1.mp4",
        
        # Episode 2
        "Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4",
        "Petrocelli2.mp4",
        "Petrocelli-Episode-2.mp4",
        "Petrocelli-Episode2.mp4",
        
        # Episode 3
        "Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4",
        "Petrocelli3.mp4",
        "Petrocelli-Episode-3.mp4",
        "Petrocelli-Episode3.mp4",
        
        # Episode 4
        "Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4",
        "Petrocelli4.mp4",
        "Petrocelli-Episode-4.mp4",
        "Petrocelli-Episode4.mp4",
        
        # Episode 5
        "Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4",
        "Petrocelli5.mp4",
        "Petrocelli-Episode-5.mp4",
        "Petrocelli-Episode5.mp4",
        
        # Episode 6
        "Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4",
        "Petrocelli6.mp4",
        "Petrocelli-Episode-6.mp4",
        "Petrocelli-Episode6.mp4",
        
        # Episode 7
        "Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4",
        "Petrocelli7.mp4",
        "Petrocelli-Episode-7.mp4",
        "Petrocelli-Episode7.mp4",
        
        # Episode 8
        "Petrocelli-Survival_2p-1080-wCredits.mp4",
        "Petrocelli8.mp4",
        "Petrocelli-Episode-8.mp4",
        "Petrocelli-Episode8.mp4",
        
        # Episode 9
        "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4",
        "Petrocelli9.mp4",
        "Petrocelli-Episode-9.mp4",
        "Petrocelli-Episode9.mp4",
        
        # Episode 10
        "Petrocelli-Once-Upon-A-Victim_2p-1080-wCredits.mp4",
        "Petrocelli10.mp4",
        "Petrocelli-Episode-10.mp4",
        "Petrocelli-Episode10.mp4",
        
        # Episode 11
        "Petrocelli-A-Deadly-Game_2p-1080-wCredits.mp4",
        "Petrocelli11.mp4",
        "Petrocelli-Episode-11.mp4",
        "Petrocelli-Episode11.mp4",
        
        # Episode 12
        "Petrocelli-The-Deadly-Trap_2p-1080-wCredits.mp4",
        "Petrocelli12.mp4",
        "Petrocelli-Episode-12.mp4",
        "Petrocelli-Episode12.mp4",
        
        # Episode 13
        "Petrocelli-The-Deadly-Double_2p-1080-wCredits.mp4",
        "Petrocelli13.mp4",
        "Petrocelli-Episode-13.mp4",
        "Petrocelli-Episode13.mp4",
        
        # Episode 14
        "Petrocelli-A-Deadly-Charade_2p-1080-wCredits.mp4",
        "Petrocelli14.mp4",
        "Petrocelli-Episode-14.mp4",
        "Petrocelli-Episode14.mp4",
        
        # Episode 15
        "Petrocelli-The-Deadly-Connection_2p-1080-wCredits.mp4",
        "Petrocelli15.mp4",
        "Petrocelli-Episode-15.mp4",
        "Petrocelli-Episode15.mp4",
        
        # Episode 16
        "Petrocelli-Death-of-a-Friend_2p-1080-wCredits.mp4",
        "Petrocelli16.mp4",
        "Petrocelli-Episode-16.mp4",
        "Petrocelli-Episode16.mp4",
        
        # Episode 17
        "Petrocelli-The-Deadly-Truth_2p-1080-wCredits.mp4",
        "Petrocelli17.mp4",
        "Petrocelli-Episode-17.mp4",
        "Petrocelli-Episode17.mp4",
        
        # Episode 18
        "Petrocelli-A-Deadly-Secret_2p-1080-wCredits.mp4",
        "Petrocelli18.mp4",
        "Petrocelli-Episode-18.mp4",
        "Petrocelli-Episode18.mp4",
        
        # Episode 19
        "Petrocelli-The-Deadly-Web_2p-1080-wCredits.mp4",
        "Petrocelli19.mp4",
        "Petrocelli-Episode-19.mp4",
        "Petrocelli-Episode19.mp4",
        
        # Episode 20
        "Petrocelli-Death-by-Design_2p-1080-wCredits.mp4",
        "Petrocelli20.mp4",
        "Petrocelli-Episode-20.mp4",
        "Petrocelli-Episode20.mp4",
        
        # Episode 21
        "Petrocelli-The-Deadly-Plan_2p-1080-wCredits.mp4",
        "Petrocelli21.mp4",
        "Petrocelli-Episode-21.mp4",
        "Petrocelli-Episode21.mp4",
        
        # Episode 22
        "Petrocelli-The-Deadly-Contract_2p-1080-wCredits.mp4",
        "Petrocelli22.mp4",
        "Petrocelli-Episode-22.mp4",
        "Petrocelli-Episode22.mp4",
        
        # Additional variations
        "Petrocelli-Once-Upon-A-Victim_2p-1080-full-credits.mp4",
        "Petrocelli-Too-Many-Alibis_2p-1080-full-credits.mp4",
        
        # Simple numbered versions
        "Petrocelli-1.mp4",
        "Petrocelli-2.mp4",
        "Petrocelli-3.mp4",
        "Petrocelli-4.mp4",
        "Petrocelli-5.mp4",
        "Petrocelli-6.mp4",
        "Petrocelli-7.mp4",
        "Petrocelli-8.mp4",
        "Petrocelli-9.mp4",
        "Petrocelli-10.mp4",
        "Petrocelli-11.mp4",
        "Petrocelli-12.mp4",
        "Petrocelli-13.mp4",
        "Petrocelli-14.mp4",
        "Petrocelli-15.mp4",
        "Petrocelli-16.mp4",
        "Petrocelli-17.mp4",
        "Petrocelli-18.mp4",
        "Petrocelli-19.mp4",
        "Petrocelli-20.mp4",
        "Petrocelli-21.mp4",
        "Petrocelli-22.mp4"
    ]
    
    existing_files = []
    
    print(f"Testing {len(all_possible_files)} possible filenames...")
    print("=" * 50)
    
    for i, filename in enumerate(all_possible_files, 1):
        if test_file_exists(filename):
            existing_files.append(filename)
            print(f"✅ {i:2d}. {filename}")
        else:
            print(f"❌ {i:2d}. {filename}")
        
        # Add a small delay to avoid overwhelming the server
        if i % 10 == 0:
            time.sleep(0.1)
    
    print(f"\n📊 SUMMARY:")
    print("=" * 40)
    print(f"Total files tested: {len(all_possible_files)}")
    print(f"Files that exist: {len(existing_files)}")
    print(f"Files missing: {len(all_possible_files) - len(existing_files)}")
    
    if existing_files:
        print(f"\n✅ EXISTING FILES:")
        for i, filename in enumerate(existing_files, 1):
            print(f"  {i:2d}. {filename}")
    
    return existing_files

if __name__ == "__main__":
    existing_files = list_all_actual_files()
    print(f"\n🎯 Found {len(existing_files)} actual files in GCS bucket") 