#!/usr/bin/env python3
"""
Exhaustive script to find ALL Petrocelli files in the GCS bucket.
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

def find_all_petrocelli_files_exhaustive():
    """Find ALL Petrocelli files using exhaustive naming patterns."""
    print("🔍 EXHAUSTIVE SEARCH FOR ALL PETROCELLI FILES")
    print("=" * 70)
    
    found_files = []
    
    # Test the 9 files we already know exist
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
    
    print("Testing known files...")
    for filename in known_files:
        if test_file_exists(filename):
            found_files.append(filename)
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename}")
    
    # Test episode number patterns for episodes 10-22
    print(f"\nTesting episode number patterns for episodes 10-22...")
    for episode_num in range(10, 23):
        episode_patterns = [
            f"Petrocelli{episode_num}.mp4",
            f"Petrocelli-{episode_num}.mp4",
            f"Petrocelli-Episode-{episode_num}.mp4",
            f"Petrocelli-Episode{episode_num}.mp4",
            f"Petrocelli-Episode-{episode_num:02d}.mp4",
            f"Petrocelli-Episode{episode_num:02d}.mp4",
            f"Petrocelli-{episode_num:02d}.mp4",
            f"Petrocelli{episode_num:02d}.mp4",
            f"Petrocelli-Episode-{episode_num}_2p-1080-wCredits.mp4",
            f"Petrocelli-Episode{episode_num}_2p-1080-wCredits.mp4",
            f"Petrocelli-{episode_num}_2p-1080-wCredits.mp4",
            f"Petrocelli{episode_num}_2p-1080-wCredits.mp4",
            f"Petrocelli-Episode-{episode_num:02d}_2p-1080-wCredits.mp4",
            f"Petrocelli-Episode{episode_num:02d}_2p-1080-wCredits.mp4",
            f"Petrocelli-{episode_num:02d}_2p-1080-wCredits.mp4",
            f"Petrocelli{episode_num:02d}_2p-1080-wCredits.mp4"
        ]
        
        for filename in episode_patterns:
            if test_file_exists(filename):
                found_files.append(filename)
                print(f"  ✅ Episode {episode_num}: {filename}")
                break
        else:
            print(f"  ❌ Episode {episode_num}: No file found")
    
    # Test common episode title patterns
    print(f"\nTesting common episode title patterns...")
    common_titles = [
        "Once-Upon-A-Victim", "Once-Upon-a-Victim", "Once-Upon-A-Victim",
        "A-Life-For-A-Life", "A-Life-for-a-Life", "A-Life-For-a-Life",
        "The-Prisoner", "The-Prisoner",
        "The-Deadly-Double", "The-Deadly-double", "The-Deadly-Double",
        "The-Deadly-Game", "The-Deadly-game", "The-Deadly-Game",
        "The-Deadly-Trap", "The-Deadly-trap", "The-Deadly-Trap",
        "The-Deadly-Victim", "The-Deadly-victim", "The-Deadly-Victim",
        "The-Deadly-Witness", "The-Deadly-witness", "The-Deadly-Witness",
        "The-Deadly-Confession", "The-Deadly-confession", "The-Deadly-Confession",
        "The-Deadly-Evidence", "The-Deadly-evidence", "The-Deadly-Evidence",
        "The-Deadly-Jury", "The-Deadly-jury", "The-Deadly-Jury",
        "The-Deadly-Verdict", "The-Deadly-verdict", "The-Deadly-Verdict",
        "The-Deadly-Sentence", "The-Deadly-sentence", "The-Deadly-Sentence",
        "The-Deadly-Appeal", "The-Deadly-appeal", "The-Deadly-Appeal",
        "The-Deadly-Retrial", "The-Deadly-retrial", "The-Deadly-Retrial"
    ]
    
    for title in common_titles:
        filename = f"Petrocelli-{title}_2p-1080-wCredits.mp4"
        if test_file_exists(filename):
            found_files.append(filename)
            print(f"  ✅ {filename}")
    
    # Test variations without credits suffix
    print(f"\nTesting variations without credits suffix...")
    for title in common_titles:
        filename = f"Petrocelli-{title}_2p-1080.mp4"
        if test_file_exists(filename):
            found_files.append(filename)
            print(f"  ✅ {filename}")
    
    # Test variations with different quality suffixes
    print(f"\nTesting different quality suffixes...")
    quality_suffixes = [
        "_2p-1080-wCredits.mp4",
        "_2p-1080-full-credits.mp4", 
        "_2p-1080.mp4",
        "_1080p-wCredits.mp4",
        "_1080p.mp4",
        "_720p-wCredits.mp4",
        "_720p.mp4",
        ".mp4"
    ]
    
    for title in common_titles:
        for suffix in quality_suffixes:
            filename = f"Petrocelli-{title}{suffix}"
            if test_file_exists(filename):
                found_files.append(filename)
                print(f"  ✅ {filename}")
                break
    
    print(f"\n📊 FINAL RESULTS:")
    print("=" * 50)
    print(f"Total files found: {len(found_files)}")
    
    if found_files:
        print(f"\n✅ ALL FOUND FILES:")
        for i, filename in enumerate(sorted(found_files), 1):
            print(f"  {i:2d}. {filename}")
    else:
        print("❌ No files found!")
    
    return found_files

if __name__ == "__main__":
    found_files = find_all_petrocelli_files_exhaustive() 