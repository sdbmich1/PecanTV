#!/usr/bin/env python3
"""
Script to help organize existing episode files into the proper folder structure.
Creates 'pecantv_series' folder with subfolders using underscores.
"""

import os
import shutil
import glob

# Base folder for series
SERIES_BASE_FOLDER = '../pecantv_series'

# Series name mappings (actual_series_name -> folder_name)
SERIES_MAPPINGS = {
    'Lone Ranger': 'lone_ranger',
    'Man with a Camera': 'man_with_a_camera',
    'Ghost Squad': 'ghost_squad',
    'Bonanza': 'bonanza',
    'Count of Monte Cristo': 'count_of_monte_cristo',
    'Commando Cody': 'commando_cody',
    'Mike Hammer': 'mike_hammer',
    'Green Hornet': 'green_hornet',
    'Count Duckula': 'count_duckula'
}

def create_series_folders():
    """Create the series folder structure."""
    if not os.path.exists(SERIES_BASE_FOLDER):
        os.makedirs(SERIES_BASE_FOLDER)
        print(f"✅ Created base folder: {SERIES_BASE_FOLDER}")
    
    for series_name, folder_name in SERIES_MAPPINGS.items():
        folder_path = os.path.join(SERIES_BASE_FOLDER, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"✅ Created folder: {folder_path}")
        else:
            print(f"ℹ️  Folder already exists: {folder_path}")

def find_episode_files():
    """Find episode files in the current directory and subdirectories."""
    episode_files = []
    
    # Look for common episode file patterns
    file_patterns = [
        '*.xlsx',
        '*.xls',
        '*.csv',
        '*.json',
        '**/*.xlsx',
        '**/*.xls',
        '**/*.csv',
        '**/*.json'
    ]
    
    for pattern in file_patterns:
        files = glob.glob(pattern, recursive=True)
        episode_files.extend(files)
    
    # Remove duplicates and filter out files in the target folder
    unique_files = []
    for file_path in episode_files:
        if not file_path.startswith(SERIES_BASE_FOLDER) and os.path.isfile(file_path):
            unique_files.append(file_path)
    
    return list(set(unique_files))

def detect_series_from_filename(filename):
    """Try to detect series name from filename."""
    filename_lower = filename.lower()
    
    for series_name, folder_name in SERIES_MAPPINGS.items():
        series_name_lower = series_name.lower()
        if series_name_lower in filename_lower:
            return series_name
    
    return None

def organize_files():
    """Organize episode files into series folders."""
    print("🔍 Finding episode files...")
    episode_files = find_episode_files()
    
    if not episode_files:
        print("❌ No episode files found")
        return
    
    print(f"📁 Found {len(episode_files)} episode files:")
    for file_path in episode_files:
        print(f"  • {file_path}")
    
    # Group files by detected series
    series_groups = {}
    unassigned_files = []
    
    for file_path in episode_files:
        filename = os.path.basename(file_path)
        series_name = detect_series_from_filename(filename)
        
        if series_name:
            if series_name not in series_groups:
                series_groups[series_name] = []
            series_groups[series_name].append(file_path)
        else:
            unassigned_files.append(file_path)
    
    # Move files to appropriate folders
    moved_count = 0
    
    for series_name, files in series_groups.items():
        folder_name = SERIES_MAPPINGS[series_name]
        folder_path = os.path.join(SERIES_BASE_FOLDER, folder_name)
        
        print(f"\n📺 Processing {series_name} ({len(files)} files):")
        
        for file_path in files:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(folder_path, filename)
            
            try:
                if os.path.exists(dest_path):
                    print(f"  ⚠️  File already exists, skipping: {filename}")
                else:
                    shutil.copy2(file_path, dest_path)
                    print(f"  ✅ Copied: {filename}")
                    moved_count += 1
            except Exception as e:
                print(f"  ❌ Error copying {filename}: {e}")
    
    # Report unassigned files
    if unassigned_files:
        print(f"\n⚠️  Unassigned files ({len(unassigned_files)}):")
        for file_path in unassigned_files:
            print(f"  • {file_path}")
        
        print("\n💡 To assign these files, you can:")
        print("  1. Rename them to include the series name")
        print("  2. Move them manually to the appropriate folder")
        print("  3. Update the SERIES_MAPPINGS in this script")
    
    print(f"\n✅ Successfully organized {moved_count} files")

def show_folder_structure():
    """Show the current folder structure."""
    print("\n📁 Current folder structure:")
    print("=" * 40)
    
    if not os.path.exists(SERIES_BASE_FOLDER):
        print("❌ Series base folder does not exist")
        return
    
    for series_name, folder_name in SERIES_MAPPINGS.items():
        folder_path = os.path.join(SERIES_BASE_FOLDER, folder_name)
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            print(f"\n📺 {series_name} ({folder_name}/):")
            if files:
                for file in files:
                    print(f"  • {file}")
            else:
                print(f"  (empty)")
        else:
            print(f"\n📺 {series_name} ({folder_name}/): (not created)")

def main():
    """Main function to organize episode files."""
    print("📁 Organizing Episode Files into Series Folders")
    print("=" * 60)
    
    # Create folder structure
    create_series_folders()
    
    # Organize files
    organize_files()
    
    # Show final structure
    show_folder_structure()
    
    print(f"\n🎉 Organization complete!")
    print(f"📁 Series folders are in: {SERIES_BASE_FOLDER}")
    print(f"💡 You can now run 'load_episodes_from_folders.py' to load episodes into the database")

if __name__ == "__main__":
    main() 