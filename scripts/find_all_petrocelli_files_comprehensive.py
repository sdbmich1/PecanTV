#!/usr/bin/env python3
"""
Comprehensive script to find ALL Petrocelli files in the GCS bucket.
"""

import requests
import time
import re

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

def find_all_petrocelli_files():
    """Find ALL Petrocelli files using comprehensive naming patterns."""
    print("🔍 Comprehensive search for ALL Petrocelli files...")
    print("=" * 70)
    
    # Start with the 9 files we know exist
    known_files = [
        "Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4",
        "Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4", 
        "Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4",
        "Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4",
        "Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4",
        "Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4",
        "Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4",
        "Petrocelli-Survival_2p-1080-wCredits.mp4",
        "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4"
    ]
    
    # Comprehensive list of possible episode titles for episodes 10-22
    episode_titles = [
        # Episode 10
        "Once-Upon-A-Victim",
        "Once-Upon-a-Victim", 
        "Once-Upon-A-Victim",
        "Once-Upon-a-Victim",
        
        # Episode 11
        "A-Deadly-Game",
        "A-Deadly-game",
        "A-Deadly-Game",
        "A-Deadly-game",
        
        # Episode 12
        "The-Deadly-Trap",
        "The-Deadly-trap",
        "The-Deadly-Trap",
        "The-Deadly-trap",
        
        # Episode 13
        "The-Deadly-Double",
        "The-Deadly-double",
        "The-Deadly-Double",
        "The-Deadly-double",
        
        # Episode 14
        "A-Deadly-Charade",
        "A-Deadly-charade",
        "A-Deadly-Charade",
        "A-Deadly-charade",
        
        # Episode 15
        "The-Deadly-Connection",
        "The-Deadly-connection",
        "The-Deadly-Connection",
        "The-Deadly-connection",
        
        # Episode 16
        "Death-of-a-Friend",
        "Death-of-a-friend",
        "Death-of-A-Friend",
        "Death-of-a-friend",
        
        # Episode 17
        "The-Deadly-Truth",
        "The-Deadly-truth",
        "The-Deadly-Truth",
        "The-Deadly-truth",
        
        # Episode 18
        "A-Deadly-Secret",
        "A-Deadly-secret",
        "A-Deadly-Secret",
        "A-Deadly-secret",
        
        # Episode 19
        "The-Deadly-Web",
        "The-Deadly-web",
        "The-Deadly-Web",
        "The-Deadly-web",
        
        # Episode 20
        "Death-by-Design",
        "Death-by-design",
        "Death-By-Design",
        "Death-by-design",
        
        # Episode 21
        "The-Deadly-Plan",
        "The-Deadly-plan",
        "The-Deadly-Plan",
        "The-Deadly-plan",
        
        # Episode 22
        "The-Deadly-Contract",
        "The-Deadly-contract",
        "The-Deadly-Contract",
        "The-Deadly-contract"
    ]
    
    # Different file extensions and naming patterns
    patterns = [
        "_2p-1080-wCredits.mp4",
        "_2p-1080-full-credits.mp4",
        "_2p-1080.mp4",
        "_1080p.mp4",
        "_HD.mp4",
        ".mp4"
    ]
    
    all_test_files = known_files.copy()
    
    # Generate all possible combinations
    for title in episode_titles:
        for pattern in patterns:
            filename = f"Petrocelli-{title}{pattern}"
            all_test_files.append(filename)
    
    # Add simple numbered patterns
    for i in range(10, 23):
        all_test_files.extend([
            f"Petrocelli{i}.mp4",
            f"Petrocelli-{i}.mp4",
            f"Petrocelli-Episode-{i}.mp4",
            f"Petrocelli-Episode{i}.mp4"
        ])
    
    # Remove duplicates
    all_test_files = list(set(all_test_files))
    
    existing_files = []
    
    print(f"Testing {len(all_test_files)} possible filenames...")
    print("=" * 50)
    
    for i, filename in enumerate(all_test_files, 1):
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
    print(f"Total files tested: {len(all_test_files)}")
    print(f"Files that exist: {len(existing_files)}")
    print(f"Files missing: {len(all_test_files) - len(existing_files)}")
    
    if existing_files:
        print(f"\n✅ EXISTING FILES:")
        for i, filename in enumerate(existing_files, 1):
            print(f"  {i:2d}. {filename}")
    
    return existing_files

if __name__ == "__main__":
    existing_files = find_all_petrocelli_files()
    print(f"\n🎯 Found {len(existing_files)} actual files in GCS bucket") 