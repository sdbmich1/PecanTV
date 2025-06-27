#!/usr/bin/env python3
"""
Script to check if the Petrocelli files with 'full-credits' suffix exist in GCS.
"""

import requests

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

def check_petrocelli_full_credits_files():
    """Check if the Petrocelli files with 'full-credits' suffix exist."""
    print("🔍 CHECKING PETROCELLI FULL-CREDITS FILES")
    print("=" * 50)
    
    # The files from Wurl metadata that we added
    full_credits_files = [
        "Petrocelli-Once-Upon-A-Victim_2p-1080-full-credits.mp4",
        "Petrocelli-Counterploy_2p-1080-full-credits.mp4",
        "Petrocelli-By-Reason-of-Madness_2p-1080-full-credits.mp4",
        "Petrocelli-A-Fallen-Idol_2p-1080-full-credits.mp4"
    ]
    
    # Also check for Edge of Evil which was mentioned in Wurl
    edge_of_evil_files = [
        "Petrocelli-Edge-of-Evil_2p-1080-full-credits.mp4",
        "Petrocelli-Edge-of-Evil_2p-1080-wCredits.mp4"
    ]
    
    print("Checking full-credits files:")
    for filename in full_credits_files:
        if test_file_exists(filename):
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename}")
    
    print("\nChecking Edge of Evil variations:")
    for filename in edge_of_evil_files:
        if test_file_exists(filename):
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename}")
    
    # Also check if there are any other variations
    print("\nChecking other possible variations:")
    variations = [
        "Petrocelli-Once-Upon-A-Victim_2p-1080-wCredits.mp4",
        "Petrocelli-Counterploy_2p-1080-wCredits.mp4",
        "Petrocelli-By-Reason-of-Madness_2p-1080-wCredits.mp4",
        "Petrocelli-A-Fallen-Idol_2p-1080-wCredits.mp4"
    ]
    
    for filename in variations:
        if test_file_exists(filename):
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename}")

if __name__ == "__main__":
    check_petrocelli_full_credits_files() 