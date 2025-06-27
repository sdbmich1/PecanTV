# Enhanced Excel/CSV Upload Script

This enhanced upload script (`upload_content_episodes_enhanced.py`) handles both Excel (XLSX/XLS) and CSV files with advanced duplicate detection and data validation features.

## Key Features

### 🎯 **Multi-Format Support**
- **Excel files**: `.xlsx`, `.xls` with multiple sheet support
- **CSV files**: Standard comma-separated values
- **Automatic detection**: Script detects file type and handles accordingly

### 🔄 **Duplicate Handling**
- **Skip duplicates**: Option to skip existing records entirely
- **Update existing**: Option to update existing records with new data
- **Smart detection**: Checks content by title, episodes by title + season + episode number
- **Detailed reporting**: Shows counts of inserted, skipped, and duplicate records

### 📊 **Data Validation**
- **Flexible column mapping**: Automatically detects common column name variations
- **Data cleaning**: Normalizes text, handles missing values, validates URLs
- **Error handling**: Continues processing even if individual rows have issues

### 🚀 **Batch Processing**
- **Single file**: Process one file at a time
- **Folder processing**: Process all Excel/CSV files in a folder
- **Pattern matching**: Use glob patterns to select specific files
- **Natural sorting**: Files are processed in logical order (e.g., 7.0.12 before 7.0.61)

## Usage Examples

### Basic Usage

```bash
# Upload a single Excel file
python upload_content_episodes_enhanced.py data.xlsx

# Upload a single CSV file
python upload_content_episodes_enhanced.py data.csv

# Upload all files in a folder
python upload_content_episodes_enhanced.py /path/to/data/folder/
```

### Advanced Options

```bash
# Specify a sheet name for Excel files
python upload_content_episodes_enhanced.py data.xlsx --sheet "Content"

# Skip duplicates instead of updating
python upload_content_episodes_enhanced.py data.xlsx --skip-duplicates

# Only process content (skip episodes)
python upload_content_episodes_enhanced.py data.xlsx --content-only

# Only process episodes (skip content)
python upload_content_episodes_enhanced.py data.xlsx --episodes-only

# Use file pattern matching
python upload_content_episodes_enhanced.py /path/to/folder/ --pattern "*7.0.*.csv"

# Dry run (show what would be uploaded without actually uploading)
python upload_content_episodes_enhanced.py data.xlsx --dry-run
```

### Batch Processing Examples

```bash
# Process all Wurl sequence files (7.0.12 to 7.0.61)
python upload_content_episodes_enhanced.py /path/to/wurl/files/ --pattern "*7.0.*.csv"

# Process all Excel files in a folder
python upload_content_episodes_enhanced.py /path/to/excel/files/ --pattern "*.xlsx"

# Process mixed file types, skipping duplicates
python upload_content_episodes_enhanced.py /path/to/mixed/files/ --skip-duplicates
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `file_path` | Path to file or folder (required) |
| `--sheet` | Sheet name for Excel files |
| `--content-only` | Only process content, skip episodes |
| `--episodes-only` | Only process episodes, skip content |
| `--skip-duplicates` | Skip duplicate records instead of updating |
| `--dry-run` | Show what would be uploaded without actually uploading |
| `--pattern` | File pattern to match (e.g., "*.csv" or "*7.0.*") |

## Expected Data Formats

### Content Columns (Auto-detected)
The script automatically detects these column name variations:

| Field | Possible Column Names |
|-------|---------------------|
| Title | `title`, `name`, `Title`, `Name`, `Internal Title` |
| Poster URL | `poster_url`, `poster`, `image_url`, `Poster URL`, `Artwork Filename` |
| Trailer URL | `trailer_url`, `trailer`, `video_url`, `Trailer URL` |
| Content URL | `content_url`, `content`, `stream_url`, `Content URL`, `Video Filename` |
| Description | `description`, `desc`, `plot`, `Description`, `Short Description` |
| Type | `type`, `content_type`, `Type`, `Entry Type` |
| Runtime | `runtime`, `duration`, `length`, `Runtime` |
| Genre | `genre`, `genres`, `category`, `Genre`, `Genre Value` |
| Rating | `rating`, `age_rating`, `Rating`, `Rating Value` |
| Release Date | `release_date`, `date`, `year`, `Release Date` |

### Episode Columns (Auto-detected)
| Field | Possible Column Names |
|-------|---------------------|
| Title | `title`, `name`, `Title`, `Name`, `Episode Title` |
| Series Title | `series_title`, `show_title`, `Series Title`, `Show Title` |
| Season Number | `season_number`, `season`, `Season Number`, `Season` |
| Episode Number | `episode_number`, `episode`, `Episode Number`, `Episode` |
| Description | `description`, `desc`, `plot`, `Description` |
| Runtime | `runtime`, `duration`, `length`, `Runtime` |
| Content URL | `content_url`, `content`, `stream_url`, `Content URL`, `Video Filename` |
| Poster URL | `poster_url`, `poster`, `image_url`, `Poster URL`, `Artwork Filename` |

## Duplicate Handling Strategies

### Content Duplicates
- **Detection**: Based on title (case-insensitive)
- **Options**:
  - `--skip-duplicates`: Skip entirely
  - Default: Update existing record with new data

### Episode Duplicates
- **Detection**: Based on title + season_number + episode_number
- **Options**:
  - `--skip-duplicates`: Skip entirely
  - Default: Update existing record with new data

## URL Construction

The script automatically constructs proper Google Cloud Storage URLs:

- **Poster images**: `https://storage.googleapis.com/pecantv_title_images/{filename}`
- **Content videos**: `https://storage.googleapis.com/pecantv_features/{filename}`
- **Trailer videos**: `https://storage.googleapis.com/pecantv_trailers/{filename}`

If URLs are already complete (start with `http`), they're used as-is.

## Data Validation & Cleaning

### Text Fields
- Strips whitespace
- Converts to string
- Handles null/NaN values

### Numeric Fields
- Runtime: Converts to integer, defaults to 0 if invalid
- Season/Episode numbers: Converts to integer, defaults to 1 if invalid

### Date Fields
- Parses various date formats
- Converts to PostgreSQL date type
- Handles invalid dates gracefully

### Content Type
- Maps "MOVIE" → "FILM"
- Validates against ["FILM", "SERIES"]
- Defaults to "FILM" if invalid

## Error Handling

- **Individual row errors**: Logged but don't stop processing
- **File read errors**: Skip file and continue with others
- **Database errors**: Rollback transaction and report error
- **Missing columns**: Use fallback values where possible

## Output & Reporting

The script provides detailed feedback:

```
📁 Found 5 files to process

📄 Processing: data1.xlsx
📊 Processing sheet: Content
🔍 Found columns: {'title': 'Title', 'poster_url': 'Artwork Filename', ...}
📝 Processing 150 content items from data1.xlsx::Content...
✅ Inserted 145 content items from data1.xlsx::Content
   Skipped: 3, Duplicates: 2

🎉 Upload Summary:
   Content: 145 inserted, 3 skipped, 2 duplicates
   Episodes: 0 inserted, 0 skipped, 0 duplicates
```

## Troubleshooting

### Common Issues

1. **"No files found"**
   - Check file path is correct
   - Verify file extensions (.xlsx, .xls, .csv)
   - Use `--pattern` to match specific files

2. **"No valid data to insert"**
   - Check column names match expected formats
   - Verify data has required fields (title for content, title+series for episodes)
   - Check for empty or invalid data

3. **"Failed to connect"**
   - Verify Neon database connection string
   - Check network connectivity
   - Ensure database is accessible

4. **"Duplicate key violation"**
   - Use `--skip-duplicates` to avoid conflicts
   - Check existing data for conflicts
   - Review duplicate detection logic

### Debug Tips

- Use `--dry-run` to see what would be processed
- Check column detection output in logs
- Review individual row error messages
- Verify data format matches expected schema

## Performance Considerations

- **Large files**: Process in smaller batches if memory issues occur
- **Many files**: Use pattern matching to process subsets
- **Network**: Ensure stable connection to Neon database
- **Memory**: Large Excel files with multiple sheets may require more RAM

## Best Practices

1. **Backup first**: Always backup database before bulk uploads
2. **Test small**: Test with small files before processing large batches
3. **Use dry-run**: Preview changes before applying them
4. **Check duplicates**: Review duplicate handling strategy for your use case
5. **Validate data**: Ensure source data is clean and properly formatted 