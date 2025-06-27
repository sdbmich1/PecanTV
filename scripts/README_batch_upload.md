# Batch CSV Upload Guide

This script automatically processes all CSV files in a folder, perfect for handling the Wurl sequence files (7.0.12 - 7.0.61).

## Usage

### Process All CSV Files in a Folder

```bash
python scripts/batch_upload_csv.py /path/to/your/csv/folder
```

### Process Specific Pattern Files

```bash
# Process only Wurl files with version 7.0.x
python scripts/batch_upload_csv.py /path/to/your/csv/folder --pattern "Wurl-File-Upload-Metadata_Version-7.0.*.csv"

# Process files with specific naming pattern
python scripts/batch_upload_csv.py /path/to/your/csv/folder --pattern "*.csv"
```

### Dry Run (Preview Only)

```bash
# See what files would be processed without uploading
python scripts/batch_upload_csv.py /path/to/your/csv/folder --dry-run
```

## Features

- **Automatic File Discovery**: Finds all CSV files in the specified folder
- **Natural Sorting**: Processes files in correct numerical order (7.0.12 before 7.0.61)
- **Pattern Matching**: Can target specific file patterns
- **Error Handling**: Continues processing even if one file fails
- **Progress Tracking**: Shows progress and summary statistics
- **Dry Run Mode**: Preview what would be processed without uploading

## Example Output

```
🚀 Starting batch CSV upload...
📁 Folder: /path/to/csv/files
📋 Found 50 CSV files:
   - Wurl-File-Upload-Metadata_Version-7.0.12.csv
   - Wurl-File-Upload-Metadata_Version-7.0.13.csv
   - Wurl-File-Upload-Metadata_Version-7.0.14.csv
   ...

📄 Processing: Wurl-File-Upload-Metadata_Version-7.0.12.csv
   📊 Read 15 rows
📝 Processing 15 content items from Wurl-File-Upload-Metadata_Version-7.0.12.csv...
🔍 Found columns: {'title': 'Title', 'poster_url': 'Artwork Filename', ...}
✅ Inserted 15 content items from Wurl-File-Upload-Metadata_Version-7.0.12.csv

🎉 Batch upload completed!
   📁 Files processed: 50/50
   📊 Total items uploaded: 750
```

## File Requirements

- **Format**: CSV files
- **Columns**: Should include Wurl standard columns (Title, Artwork Filename, Video Filename, etc.)
- **Encoding**: UTF-8 recommended
- **Naming**: Can be any pattern, but natural sorting will work best with consistent naming

## Safety Features

- **Conflict Resolution**: Updates existing records instead of creating duplicates
- **Transaction Safety**: Each file is processed in its own transaction
- **Error Recovery**: Continues processing remaining files if one fails
- **Data Validation**: Skips invalid rows and reports errors

## Tips

1. **Test First**: Use `--dry-run` to see what files will be processed
2. **Backup**: Make sure your database is backed up before large batch uploads
3. **Monitor**: Watch the output for any errors or warnings
4. **Pattern Matching**: Use specific patterns to process only certain files
5. **Folder Structure**: Keep all CSV files in one folder for easy processing 