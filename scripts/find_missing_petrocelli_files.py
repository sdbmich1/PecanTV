#!/usr/bin/env python3
"""
Script to find the missing 14 Petrocelli files by testing ALL possible naming patterns.
"""

import requests
import re
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

def find_missing_petrocelli_files():
    """Find all Petrocelli files by testing comprehensive naming patterns."""
    print("🔍 Finding ALL Petrocelli files with comprehensive pattern testing...")
    print("=" * 70)
    
    discovered_files = []
    
    # First, let's test the simple numbered patterns (Petrocelli1.mp4, etc.)
    print("Testing simple numbered patterns...")
    for i in range(1, 23):
        filename = f"Petrocelli{i}.mp4"
        if test_file_exists(filename):
            discovered_files.append(filename)
            print(f"✅ Found: {filename}")
        time.sleep(0.1)  # Small delay to be respectful
    
    # Test variations with underscores
    print("\nTesting underscore variations...")
    for i in range(1, 23):
        patterns = [
            f"Petrocelli_{i}.mp4",
            f"Petrocelli_Episode_{i}.mp4",
            f"Petrocelli_Ep_{i}.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test variations with dashes
    print("\nTesting dash variations...")
    for i in range(1, 23):
        patterns = [
            f"Petrocelli-Episode-{i}.mp4",
            f"Petrocelli-Ep-{i}.mp4",
            f"Petrocelli-{i}.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test variations with leading zeros
    print("\nTesting leading zero variations...")
    for i in range(1, 23):
        patterns = [
            f"Petrocelli{i:02d}.mp4",
            f"Petrocelli-Episode-{i:02d}.mp4",
            f"Petrocelli-Ep-{i:02d}.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test variations with "Episode" spelled out
    print("\nTesting 'Episode' variations...")
    for i in range(1, 23):
        patterns = [
            f"Petrocelli-Episode-{i}.mp4",
            f"Petrocelli-Episode{i}.mp4",
            f"Petrocelli_Episode_{i}.mp4",
            f"Petrocelli_Episode{i}.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    # Test variations with different quality suffixes
    print("\nTesting quality suffix variations...")
    for i in range(1, 23):
        base_patterns = [
            f"Petrocelli{i}",
            f"Petrocelli-Episode-{i}",
            f"Petrocelli-Ep-{i}"
        ]
        suffixes = [
            ".mp4",
            "_1080p.mp4",
            "_720p.mp4",
            "_HD.mp4",
            "_2p-1080-wCredits.mp4",
            "_2p-1080-full-credits.mp4"
        ]
        for base in base_patterns:
            for suffix in suffixes:
                pattern = base + suffix
                if test_file_exists(pattern):
                    discovered_files.append(pattern)
                    print(f"✅ Found: {pattern}")
                time.sleep(0.1)
    
    # Test some common episode titles that might be used
    print("\nTesting common episode title patterns...")
    episode_titles = [
        "A-Deadly-Game", "The-Deadly-Trap", "The-Deadly-Double", "A-Deadly-Charade",
        "The-Deadly-Connection", "Death-of-a-Friend", "The-Deadly-Truth", "A-Deadly-Secret",
        "The-Deadly-Web", "Death-by-Design", "The-Deadly-Plan", "A-Deadly-Alliance",
        "The-Deadly-Contract", "Death-in-Small-Doses", "Shadow-of-a-Doubt"
    ]
    
    for title in episode_titles:
        patterns = [
            f"Petrocelli-{title}.mp4",
            f"Petrocelli-{title}_2p-1080-wCredits.mp4",
            f"Petrocelli-{title}_2p-1080-full-credits.mp4",
            f"Petrocelli-{title}_1080p.mp4",
            f"Petrocelli-{title}_720p.mp4"
        ]
        for pattern in patterns:
            if test_file_exists(pattern):
                discovered_files.append(pattern)
                print(f"✅ Found: {pattern}")
            time.sleep(0.1)
    
    return discovered_files

def analyze_results(files):
    """Analyze the results and provide insights."""
    print(f"\n📊 Analysis Results:")
    print("=" * 50)
    print(f"Total files found: {len(files)}")
    
    if len(files) == 22:
        print("🎉 SUCCESS: Found all 22 episodes!")
    elif len(files) > 22:
        print(f"⚠️  Found {len(files)} files (more than expected 22)")
    else:
        print(f"❌ Found only {len(files)} files (missing {22 - len(files)} files)")
    
    print(f"\n📋 All discovered files:")
    for i, file in enumerate(sorted(files), 1):
        print(f"  {i:2d}. {file}")
    
    # Try to map to episode numbers
    print(f"\n🔍 Episode mapping attempt:")
    episode_mapping = {}
    
    for file in files:
        # Extract episode number from various patterns
        number_match = re.search(r'Petrocelli(?:[-_]?(?:Episode|Ep)?[-_]?)?(\d+)', file)
        if number_match:
            episode_num = int(number_match.group(1))
            episode_mapping[episode_num] = file
            print(f"  Episode {episode_num}: {file}")
    
    missing_episodes = []
    for i in range(1, 23):
        if i not in episode_mapping:
            missing_episodes.append(i)
    
    if missing_episodes:
        print(f"\n❌ Missing episodes: {missing_episodes}")
    else:
        print(f"\n✅ All episodes mapped!")
    
    return episode_mapping, missing_episodes

if __name__ == "__main__":
    discovered_files = find_missing_petrocelli_files()
    episode_mapping, missing_episodes = analyze_results(discovered_files)
    
    print(f"\n🎯 Summary:")
    print(f"Files found: {len(discovered_files)}/22")
    print(f"Episodes mapped: {len(episode_mapping)}/22")
    print(f"Missing episodes: {len(missing_episodes)}")
    
    if missing_episodes:
        print(f"\n💡 Suggestions:")
        print("1. Check if files are in a different GCS bucket or folder")
        print("2. Verify the actual naming convention used")
        print("3. Check if files need to be uploaded to GCS")
        print("4. Look for files in local storage that haven't been uploaded yet") 