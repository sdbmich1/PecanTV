# Excel/CSV Data Upload Guide

This script helps you upload film and episode data from Excel or CSV files on Dropbox to your Neon database. It uses the same logic as the previous Google Sheets episode script.

## Prerequisites

1. **Download your Excel or CSV files from Dropbox** to your local machine
2. **Make sure the files are in a supported format** (.xlsx, .xls, .csv)

## Supported File Formats

- **Excel files**: `.xlsx`, `.xls`
- **CSV files**: `.csv`

## Usage

### Upload Content (Movies/Shows)

```bash
# Excel file
python scripts/upload_from_excel.py /path/to/your/file.xlsx --type content

# CSV file
python scripts/upload_from_excel.py /path/to/your/file.csv --type content
```

### Upload Episodes

```bash
# Excel file
python scripts/upload_from_excel.py /path/to/your/file.xlsx --type episodes

# CSV file
python scripts/upload_from_excel.py /path/to/your/file.csv --type episodes
```

### Specify a Sheet (Excel files only)

```bash
python scripts/upload_from_excel.py /path/to/your/file.xlsx --type content --sheet "Sheet1"
```

**Note**: The `--sheet` parameter is ignored for CSV files since they don't have multiple sheets.

## Expected Column Formats

### For Content (Movies/Shows)

The script will automatically detect these column names (case-insensitive):

| Expected Field | Possible Column Names |
|----------------|----------------------|
| Title | `title`, `name`, `Title`, `Name` |
| Poster URL | `poster_url`, `poster`, `image_url`, `Poster URL` |
| Trailer URL | `trailer_url`, `trailer`, `video_url`, `Trailer URL` |
| Content URL | `content_url`, `content`, `stream_url`, `Content URL` |
| Description | `description`, `desc`, `plot`, `Description` |
| Type | `type`, `content_type`, `Type` |
| Runtime | `runtime`, `duration`, `length`, `Runtime` |
| Genre | `genre`, `genres`, `category`, `Genre` |
| Rating | `rating`, `age_rating`, `Rating` |
| Release Date | `release_date`, `date`, `year`, `Release Date` |

### For Episodes

| Expected Field | Possible Column Names |
|----------------|----------------------|
| Series Title | `series_title`, `show_title`, `series`, `Series Title`, `series_name` |
| Episode Number | `episode_number`, `episode`, `number`, `Episode Number`, `episode_num` |
| Season Number | `season_number`, `season`, `Season Number`, `season_num` |
| Title | `title`, `episode_title`, `name`, `Title`, `episode_name` |
| Description | `description`, `desc`, `plot`, `Description` |
| Runtime | `runtime`, `duration`, `length`, `Runtime` |
| Content URL | `content_url`, `video_url`, `stream_url`, `Content URL` |
| Thumbnail URL | `thumbnail_url`, `thumbnail`, `image_url`, `Thumbnail URL` |

## Important Notes

1. **Content Type**: For content, use `MOVIE`, `SERIES`, or `EPISODE` in the type column
2. **Genres**: Must match existing genres in the database (case-insensitive)
3. **Ratings**: Must match existing ratings in the database (case-insensitive)
4. **Series for Episodes**: The series title must exist in the content table as a `SERIES` type
5. **Duplicate Handling**: 
   - Content: Updates existing records if they have the same title
   - Episodes: Updates existing records if they have the same series_id, season_number, and episode_number combination

## Database Schema

The script uses the exact same database schema as the previous Google Sheets script:

### Content Table
```sql
CREATE TABLE content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    poster_url TEXT,
    trailer_url TEXT,
    content_url TEXT,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    runtime INTEGER,
    genre_id INTEGER REFERENCES genres(id),
    rating_id INTEGER REFERENCES ratings(id),
    release_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Episodes Table
```sql
CREATE TABLE episodes (
    id SERIAL PRIMARY KEY,
    series_id INTEGER NOT NULL REFERENCES content(id),
    season_number INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content_url TEXT,
    thumbnail_url TEXT,
    runtime INTEGER,
    air_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(series_id, season_number, episode_number)
);
```

## Example Excel Structure

### Content Sheet Example:
```
| Title | Type | Genre | Rating | Runtime | Description | Poster URL | Content URL |
|-------|------|-------|--------|---------|-------------|------------|-------------|
| The Matrix | MOVIE | Action | PG-13 | 136 | A computer hacker learns... | https://... | https://... |
| Breaking Bad | SERIES | Drama | TV-MA | 45 | A high school chemistry teacher... | https://... | https://... |
```

### Episodes Sheet Example:
```
| Series Title | Episode Number | Season Number | Title | Description | Runtime | Content URL |
|-------------|----------------|---------------|-------|-------------|---------|-------------|
| Breaking Bad | 1 | 1 | Pilot | Walter White learns he has cancer... | 58 | https://... |
| Breaking Bad | 2 | 1 | Cat's in the Bag | Walt and Jesse deal with the aftermath... | 48 | https://... |
```

## Troubleshooting

1. **"Series not found"**: Make sure the series exists in the content table with type `SERIES`
2. **"Genre not found"**: Check that the genre name matches exactly (case-insensitive)
3. **"Rating not found"**: Check that the rating code matches exactly (case-insensitive)
4. **Column detection issues**: Make sure your column headers match one of the expected names

## Safety Features

- The script will skip rows with missing titles
- Invalid data types are handled gracefully
- Existing records are updated rather than duplicated
- All operations are wrapped in database transactions
- Uses the same proven logic as the Google Sheets script 