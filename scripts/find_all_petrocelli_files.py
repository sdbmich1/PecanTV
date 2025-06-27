#!/usr/bin/env python3
"""
Script to find ALL Petrocelli files by testing every possible naming pattern.
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

def find_all_petrocelli_files():
    """Find ALL Petrocelli files by testing comprehensive naming patterns."""
    print("🔍 Finding ALL Petrocelli files with comprehensive pattern testing...")
    print("=" * 70)
    
    discovered_files = []
    
    # Test simple numbered patterns first
    print("Testing simple numbered patterns...")
    for i in range(1, 23):
        patterns = [
            f"Petrocelli{i}.mp4",
            f"Petrocelli-{i}.mp4",
            f"Petrocelli_Episode_{i}.mp4",
            f"Petrocelli-Episode-{i}.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test with leading zeros
    print("\nTesting with leading zeros...")
    for i in range(1, 23):
        patterns = [
            f"Petrocelli{i:02d}.mp4",
            f"Petrocelli-{i:02d}.mp4",
            f"Petrocelli_Episode_{i:02d}.mp4",
            f"Petrocelli-Episode-{i:02d}.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test episode title patterns
    print("\nTesting episode title patterns...")
    episode_titles = [
        "Deadly-Journey", "Face-of-Evil", "Four-the-Hard-Way", "Once-Upon-A-Victim",
        "Shadow-of-Fear", "The-Night-Visitor", "Too-Many-Alibis", "Shadow-of-a-Doubt",
        "Death-in-Small-Doses", "Survival", "A-Deadly-Game", "The-Deadly-Trap",
        "The-Deadly-Double", "A-Deadly-Charade", "The-Deadly-Connection",
        "Death-of-a-Friend", "The-Deadly-Truth", "A-Deadly-Secret", "The-Deadly-Web",
        "Death-by-Design", "The-Deadly-Plan", "A-Deadly-Alliance", "The-Deadly-Contract",
        # Add more possible titles
        "Death-of-a-Small-Town", "The-Deadly-Game", "A-Deadly-Trap", "The-Deadly-Secret",
        "Death-in-the-Family", "The-Deadly-Truth", "A-Deadly-Lie", "The-Deadly-Web",
        "Death-by-Natural-Causes", "The-Deadly-Plan", "A-Deadly-Mistake", "The-Deadly-Contract",
        "Death-of-a-Salesman", "The-Deadly-Truth", "A-Deadly-Secret", "The-Deadly-Web",
        "Death-by-Design", "The-Deadly-Plan", "A-Deadly-Alliance", "The-Deadly-Contract"
    ]
    
    for title in episode_titles:
        patterns = [
            f"Petrocelli-{title}.mp4",
            f"Petrocelli-{title}_2p-1080-wCredits.mp4",
            f"Petrocelli-{title}_2p-1080-full-credits.mp4",
            f"Petrocelli-{title}_1080p.mp4",
            f"Petrocelli-{title}_720p.mp4",
            f"Petrocelli-{title}_HD.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test variations with different separators
    print("\nTesting variations with different separators...")
    for i in range(1, 23):
        patterns = [
            f"Petrocelli_{i}.mp4",
            f"Petrocelli_Ep_{i}.mp4",
            f"Petrocelli_Episode_{i}.mp4",
            f"Petrocelli-Ep-{i}.mp4",
            f"Petrocelli-Episode-{i}.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test quality variations
    print("\nTesting quality variations...")
    for i in range(1, 23):
        base_patterns = [
            f"Petrocelli{i}",
            f"Petrocelli-{i}",
            f"Petrocelli_Episode_{i}",
            f"Petrocelli-Episode-{i}"
        ]
        suffixes = [
            ".mp4",
            "_1080p.mp4",
            "_720p.mp4",
            "_HD.mp4",
            "_2p-1080-wCredits.mp4",
            "_2p-1080-full-credits.mp4",
            "_1080-wCredits.mp4",
            "_1080-full-credits.mp4"
        ]
        for base in base_patterns:
            for suffix in suffixes:
                pattern = base + suffix
                if test_file_exists(pattern):
                    discovered_files.append(pattern)
                    print(f"✅ Found: {pattern}")
                time.sleep(0.1)
    
    # Remove duplicates and sort
    discovered_files = sorted(list(set(discovered_files)))
    
    print(f"\n📊 SUMMARY:")
    print("=" * 50)
    print(f"Total unique files found: {len(discovered_files)}")
    
    if len(discovered_files) >= 22:
        print("🎉 SUCCESS: Found enough files for all 22 episodes!")
    elif len(discovered_files) >= 15:
        print(f"✅ Good progress: Found {len(discovered_files)} files")
    else:
        print(f"⚠️  Still need more files: Found {len(discovered_files)} files")
    
    print(f"\n📋 All discovered files:")
    for i, file in enumerate(discovered_files, 1):
        print(f"  {i:2d}. {file}")
    
    return discovered_files

if __name__ == "__main__":
    discovered_files = find_all_petrocelli_files() 