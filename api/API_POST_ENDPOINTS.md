# PecanTV API POST Endpoints Guide

This guide explains how to post new data to the PecanTV API using the available POST endpoints.

## Available POST Endpoints

### 1. Create New Content
**Endpoint:** `POST /content`

Creates new films or series in the database.

#### Request Body Schema
```json
{
  "title": "string (required)",
  "posterURL": "string (optional)",
  "trailerURL": "string (required)",
  "contentURL": "string (optional)",
  "description": "string (optional)",
  "type": "FILM" | "SERIES (required)",
  "runtime": "integer (required, in minutes)",
  "genreId": "integer (optional)",
  "ratingId": "integer (optional)",
  "releaseDate": "string (optional, YYYY-MM-DD format)"
}
```

#### Example: Create a Film
```bash
curl -X POST "http://localhost:8000/content" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example Film",
    "posterURL": "https://storage.googleapis.com/pecantv_title_images/example-poster.jpg",
    "trailerURL": "https://storage.googleapis.com/pecantv_trailers/example-trailer.mp4",
    "contentURL": "https://storage.googleapis.com/pecantv_features/example-film.mp4",
    "description": "An example film description",
    "type": "FILM",
    "runtime": 120,
    "genreId": 1,
    "ratingId": 1,
    "releaseDate": "2024-01-01"
  }'
```

#### Example: Create a Series
```bash
curl -X POST "http://localhost:8000/content" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example Series",
    "posterURL": "https://storage.googleapis.com/pecantv_title_images/example-series-poster.jpg",
    "trailerURL": "https://storage.googleapis.com/pecantv_trailers/example-series-trailer.mp4",
    "contentURL": null,
    "description": "An example series description",
    "type": "SERIES",
    "runtime": 60,
    "genreId": 1,
    "ratingId": 1,
    "releaseDate": "2024-01-01"
  }'
```

### 2. Create New Episode
**Endpoint:** `POST /episodes`

Creates new episodes for existing series.

#### Request Body Schema
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "seasonNumber": "integer (required)",
  "episodeNumber": "integer (required)",
  "runtime": "integer (optional, in minutes)",
  "contentURL": "string (optional)",
  "posterURL": "string (optional)",
  "thumbnailURL": "string (optional)",
  "airDate": "string (optional, YYYY-MM-DD format)",
  "seriesId": "integer (required)",
  "contentUuid": "string (required, UUID of the series)"
}
```

#### Example: Create an Episode
```bash
curl -X POST "http://localhost:8000/episodes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example Episode",
    "description": "An example episode description",
    "seasonNumber": 1,
    "episodeNumber": 1,
    "runtime": 45,
    "contentURL": "https://storage.googleapis.com/pecantv_series/example_series/Episode1.mp4",
    "posterURL": "https://storage.googleapis.com/pecantv_title_images/example-episode-poster.jpg",
    "thumbnailURL": "https://storage.googleapis.com/pecantv_title_images/example-episode-thumbnail.jpg",
    "airDate": "2024-01-01",
    "seriesId": 1,
    "contentUuid": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

## URL Patterns for Different Content Types

### Films
- **Content URL**: `https://storage.googleapis.com/pecantv_features/{filename}`
- **Poster URL**: `https://storage.googleapis.com/pecantv_title_images/{filename}`
- **Trailer URL**: `https://storage.googleapis.com/pecantv_trailers/{filename}`

### Series Episodes
- **Content URL**: `https://storage.googleapis.com/pecantv_series/{series_folder}/{filename}`
- **Poster URL**: `https://storage.googleapis.com/pecantv_title_images/{filename}`

## Getting Available Genres and Ratings

Before creating content, you may want to get the available genres and ratings:

### Get Genres
```bash
curl "http://localhost:8000/genres"
```

### Get Ratings
```bash
curl "http://localhost:8000/ratings"
```

## Python Example

See `post_content_example.py` for a complete Python example that demonstrates:
- Fetching available genres and ratings
- Creating a new film
- Creating a new series
- Creating episodes for the series

## Response Format

Successful POST requests return the created object with all fields including:
- `id`: Database ID
- `uuid`: Unique identifier
- `createdAt`: Creation timestamp
- `updatedAt`: Last update timestamp
- All the fields you provided in the request

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include a `detail` field with the error message.

## Authentication

Currently, these endpoints don't require authentication, but in a production environment, you should add authentication middleware.

## Best Practices

1. **URL Validation**: Ensure all URLs point to valid Google Cloud Storage locations
2. **Content Types**: Use "FILM" for movies and "SERIES" for TV shows
3. **Runtime**: Provide runtime in minutes
4. **Dates**: Use YYYY-MM-DD format for dates
5. **UUIDs**: For episodes, use the UUID of the parent series
6. **File Naming**: Follow the established naming conventions for your GCS buckets

## Testing the Endpoints

You can test these endpoints using:
- The provided Python script (`post_content_example.py`)
- curl commands (examples above)
- Postman or similar API testing tools
- Your application's HTTP client

## Notes

- The API automatically generates UUIDs for new content
- Timestamps are automatically set to the current time
- All URLs should follow the established GCS bucket patterns
- Content types are validated against the `ContentType` enum 