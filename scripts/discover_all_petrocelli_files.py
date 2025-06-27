#!/usr/bin/env python3
"""
Script to comprehensively discover ALL Petrocelli files in GCS bucket.
"""

import requests
import re
from urllib.parse import urljoin

# Base URL for Petrocelli files in GCS
BASE_URL = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

def discover_all_petrocelli_files():
    """Discover ALL Petrocelli files in the GCS bucket."""
    print("🔍 Comprehensively discovering ALL Petrocelli files in GCS bucket...")
    print("=" * 70)
    
    discovered_files = []
    
    # First, let's try to get a directory listing if possible
    # Note: GCS doesn't provide directory listings via HTTP, so we'll need to test patterns
    
    # Let's try a systematic approach - test common naming patterns
    print("Testing systematic naming patterns...")
    
    # Pattern 1: Petrocelli-{Episode-Title}_2p-1080-wCredits.mp4
    # Pattern 2: Petrocelli-{Episode-Title}_2p-1080-full-credits.mp4
    # Pattern 3: Petrocelli{Number}.mp4
    # Pattern 4: Petrocelli-Episode-{Number}.mp4
    
    # Let's test episode numbers 1-22 with various patterns
    for episode_num in range(1, 23):
        patterns_to_test = [
            f"Petrocelli{episode_num}.mp4",
            f"Petrocelli-Episode-{episode_num}.mp4",
            f"Petrocelli-{episode_num}.mp4",
            f"Petrocelli-Episode{episode_num}.mp4"
        ]
        
        for pattern in patterns_to_test:
            test_url = BASE_URL + pattern
            try:
                response = requests.head(test_url, timeout=10)
                if response.status_code == 200:
                    discovered_files.append(pattern)
                    print(f"✅ Episode {episode_num}: {pattern}")
                    break  # Found one for this episode, move to next
            except Exception as e:
                continue
    
    # Now let's test some known episode titles that might exist
    episode_titles = [
        "Deadly-Journey",
        "Face-of-Evil", 
        "Four-the-Hard-Way",
        "Once-Upon-A-Victim",
        "Shadow-of-Fear",
        "The-Night-Visitor",
        "Too-Many-Alibis",
        "Shadow-of-a-Doubt",
        "Death-in-Small-Doses",
        "A-Deadly-Game",
        "The-Deadly-Trap",
        "Death-in-Small-Doses",
        "The-Deadly-Double",
        "A-Deadly-Charade",
        "The-Deadly-Connection",
        "Death-of-a-Friend",
        "The-Deadly-Truth",
        "A-Deadly-Secret",
        "The-Deadly-Web",
        "Death-by-Design",
        "The-Deadly-Plan",
        "A-Deadly-Alliance",
        "The-Deadly-Contract"
    ]
    
    print(f"\nTesting episode title patterns...")
    for title in episode_titles:
        patterns_to_test = [
            f"Petrocelli-{title}_2p-1080-wCredits.mp4",
            f"Petrocelli-{title}_2p-1080-full-credits.mp4",
            f"Petrocelli-{title}.mp4"
        ]
        
        for pattern in patterns_to_test:
            test_url = BASE_URL + pattern
            try:
                response = requests.head(test_url, timeout=10)
                if response.status_code == 200:
                    if pattern not in discovered_files:
                        discovered_files.append(pattern)
                        print(f"✅ Found: {pattern}")
            except Exception as e:
                continue
    
    # Let's also try some variations we might have missed
    print(f"\nTesting additional variations...")
    additional_patterns = [
        "Petrocelli1.mp4", "Petrocelli2.mp4", "Petrocelli3.mp4", "Petrocelli4.mp4", "Petrocelli5.mp4",
        "Petrocelli6.mp4", "Petrocelli7.mp4", "Petrocelli8.mp4", "Petrocelli9.mp4", "Petrocelli10.mp4",
        "Petrocelli11.mp4", "Petrocelli12.mp4", "Petrocelli13.mp4", "Petrocelli14.mp4", "Petrocelli15.mp4",
        "Petrocelli16.mp4", "Petrocelli17.mp4", "Petrocelli18.mp4", "Petrocelli19.mp4", "Petrocelli20.mp4",
        "Petrocelli21.mp4", "Petrocelli22.mp4"
    ]
    
    for pattern in additional_patterns:
        test_url = BASE_URL + pattern
        try:
            response = requests.head(test_url, timeout=10)
            if response.status_code == 200:
                if pattern not in discovered_files:
                    discovered_files.append(pattern)
                    print(f"✅ Found: {pattern}")
        except Exception as e:
            continue
    
    return discovered_files

def analyze_discovered_files(files):
    """Analyze the discovered files and suggest episode mappings."""
    print(f"\n📋 Analysis of discovered files:")
    print("=" * 50)
    print(f"Total files found: {len(files)}")
    
    if len(files) == 22:
        print("🎉 Found all 22 episodes!")
    elif len(files) > 22:
        print(f"⚠️  Found {len(files)} files (more than expected 22)")
    else:
        print(f"❌ Found only {len(files)} files (expected 22)")
    
    print("\nDiscovered files:")
    for i, file in enumerate(sorted(files), 1):
        print(f"  {i:2d}. {file}")
    
    # Try to map files to episode numbers
    print(f"\n🔍 Attempting to map files to episode numbers...")
    episode_mapping = {}
    
    for file in files:
        # Try to extract episode number from filename
        if "Petrocelli" in file:
            # Look for patterns like Petrocelli1.mp4, Petrocelli-Episode-1.mp4, etc.
            number_match = re.search(r'Petrocelli(?:-Episode-)?(\d+)', file)
            if number_match:
                episode_num = int(number_match.group(1))
                episode_mapping[episode_num] = file
                print(f"  Episode {episode_num}: {file}")
    
    return episode_mapping

if __name__ == "__main__":
    discovered_files = discover_all_petrocelli_files()
    episode_mapping = analyze_discovered_files(discovered_files)
    
    print(f"\n📊 Summary:")
    print(f"Files discovered: {len(discovered_files)}")
    print(f"Episodes mapped: {len(episode_mapping)}")
    
    if episode_mapping:
        print(f"\n✅ Episode mapping found:")
        for episode_num in sorted(episode_mapping.keys()):
            print(f"  Episode {episode_num}: {episode_mapping[episode_num]}")
    else:
        print(f"\n❌ No clear episode mapping found. Manual mapping required.") 