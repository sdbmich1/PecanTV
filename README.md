# PecanTV - Classic TV Streaming App

A modern streaming platform for classic television series, featuring a FastAPI backend with PostgreSQL database and an iOS mobile app frontend.

## 🎬 Overview

PecanTV provides access to classic TV series like Dragnet, Commando Cody, Petrocelli, and many more. The platform features:

- **FastAPI Backend**: RESTful API with authentication, favorites, and content management
- **PostgreSQL Database**: Robust data storage with proper relationships
- **iOS App**: Native mobile experience for streaming classic content
- **Google Cloud Storage**: Scalable media file hosting
- **Static File Serving**: Local development media serving

## 🏗️ Architecture

```
PecanTV App
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints and configuration
│   ├── models.py          # SQLAlchemy database models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── crud.py            # Database operations
│   ├── database.py        # Database connection setup
│   └── url_utils.py       # URL normalization utilities
├── scripts/               # Database maintenance scripts
├── pecantv_series/        # Local media files (development)
└── iOS App/              # Native iOS application
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database (Neon recommended)
- iOS development environment (Xcode)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd pecantv_app
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
cd api && pip install -r requirements.txt
```

### 3. Database Setup

The app uses a Neon PostgreSQL database. Environment variables are configured for:
- Database connection
- JWT authentication
- API configuration

### 4. Run the API

```bash
cd api
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get all content
curl http://localhost:8000/content

# Get series episodes
curl http://localhost:8000/series/68/episodes
```

## 🌐 Accessing the API from Different Machines

### Local Network Access

To access the API from other machines on your local network:

1. **Find Your Local IP Address**
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows
   ipconfig | findstr "IPv4"
   ```

2. **Update API Configuration**
   In `api/main.py`, change the host from `127.0.0.1` to `0.0.0.0`:
   ```python
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

3. **Access from Other Machines**
   ```bash
   # From another machine on the same network
   curl http://YOUR_LOCAL_IP:8000/health
   curl http://YOUR_LOCAL_IP:8000/content
   ```

### Using ngrok for External Access

To access the API from anywhere on the internet:

1. **Install ngrok**
   ```bash
   # Download from https://ngrok.com/
   # Or install via package manager
   brew install ngrok  # macOS
   ```

2. **Start ngrok Tunnel**
   ```bash
   # After starting your API server
   ngrok http 8000
   ```

3. **Use the ngrok URL**
   ```bash
   # ngrok will provide a public URL like:
   # https://abc123.ngrok.io
   
   curl https://abc123.ngrok.io/health
   curl https://abc123.ngrok.io/content
   ```

### Production Deployment

For production access, deploy to a cloud platform:

1. **Render (Recommended)**
   ```bash
   # Follow DEPLOYMENT.md for Render setup
   # Your API will be available at:
   # https://your-app-name.onrender.com
   ```

2. **Railway**
   ```bash
   # Deploy to Railway for automatic HTTPS
   # https://your-app-name.railway.app
   ```

3. **Vercel**
   ```bash
   # Deploy to Vercel for serverless functions
   # https://your-app-name.vercel.app
   ```

### API Client Examples

#### cURL Examples
```bash
# Health check
curl -X GET "https://your-api-url.com/health"

# Get all content
curl -X GET "https://your-api-url.com/content"

# Get specific series episodes
curl -X GET "https://your-api-url.com/series/68/episodes"

# Search content
curl -X GET "https://your-api-url.com/search?q=dragnet"

# Get user favorites (requires authentication)
curl -X GET "https://your-api-url.com/favorites/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### JavaScript/Node.js
```javascript
const API_BASE_URL = 'https://your-api-url.com';

// Health check
const health = await fetch(`${API_BASE_URL}/health`);
console.log(await health.json());

// Get all content
const content = await fetch(`${API_BASE_URL}/content`);
const contentData = await content.json();

// Get series episodes
const episodes = await fetch(`${API_BASE_URL}/series/68/episodes`);
const episodesData = await episodes.json();

// Search content
const search = await fetch(`${API_BASE_URL}/search?q=dragnet`);
const searchResults = await search.json();
```

#### Python
```python
import requests

API_BASE_URL = 'https://your-api-url.com'

# Health check
response = requests.get(f'{API_BASE_URL}/health')
print(response.json())

# Get all content
response = requests.get(f'{API_BASE_URL}/content')
content = response.json()

# Get series episodes
response = requests.get(f'{API_BASE_URL}/series/68/episodes')
episodes = response.json()

# Search content
response = requests.get(f'{API_BASE_URL}/search', params={'q': 'dragnet'})
search_results = response.json()
```

#### iOS Swift
```swift
let apiBaseURL = "https://your-api-url.com"

// Health check
let healthURL = URL(string: "\(apiBaseURL)/health")!
let healthTask = URLSession.shared.dataTask(with: healthURL) { data, response, error in
    if let data = data {
        let health = try? JSONSerialization.jsonObject(with: data)
        print(health)
    }
}
healthTask.resume()

// Get content
let contentURL = URL(string: "\(apiBaseURL)/content")!
let contentTask = URLSession.shared.dataTask(with: contentURL) { data, response, error in
    if let data = data {
        let content = try? JSONSerialization.jsonObject(with: data)
        print(content)
    }
}
contentTask.resume()
```

### Authentication for External Access

When accessing from external clients, you may need to handle authentication:

1. **Register a User**
   ```bash
   curl -X POST "https://your-api-url.com/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123"}'
   ```

2. **Login to Get JWT Token**
   ```bash
   curl -X POST "https://your-api-url.com/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "password123"}'
   ```

3. **Use JWT Token for Protected Endpoints**
   ```bash
   curl -X GET "https://your-api-url.com/favorites/1" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

### CORS Configuration

The API includes CORS configuration for cross-origin requests:

```python
# In api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables for External Access

Update your environment variables for external access:

```bash
# .env file
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# For production, consider:
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ORIGINS=https://your-frontend-domain.com
```

## 📱 iOS App Setup

1. Open the iOS project in Xcode
2. Update the API base URL to point to your backend
3. Build and run on device or simulator

## 🗄️ Accessing and Using Neon Database

PecanTV uses [Neon](https://neon.tech/) for managed PostgreSQL hosting.

### How to Access Your Neon Database

1. **Log in to Neon**  
   Go to [https://console.neon.tech/](https://console.neon.tech/) and sign in.

2. **Select Your Project**  
   Click on your PecanTV project in the dashboard.

3. **Find Connection Details**  
   - In the project dashboard, look for the "Connection Details" section.
   - You'll see a connection string like:
     ```
     postgresql://<user>:<password>@<host>/<database>?sslmode=require
     ```
   - Example:
     ```
     postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
     ```

4. **Copy the Connection String**  
   Use the copy button to copy the full string.

5. **Set the Environment Variable**  
   - Locally, you can set it in your shell:
     ```bash
     export DATABASE_URL="postgresql://..."
     ```
   - Or add it to your `.env` file in the `api/` directory:
     ```
     DATABASE_URL=postgresql://...
     ```

6. **Use in Your Application**  
   The FastAPI backend will automatically use this environment variable for all database operations.

7. **Query and Manage Data**  
   - Use the Neon dashboard's SQL editor to run queries, view tables, and manage your schema.
   - You can also create branches, reset data, or monitor performance from the dashboard.

### 🌐 Calling Neon API from Netlify or Webhooks

#### Option 1: Direct API Calls from Netlify Functions

Create a Netlify function that calls your Neon-hosted API:

**File: `netlify/functions/api-proxy.js`**
```javascript
const axios = require('axios');

exports.handler = async (event, context) => {
  // Get API URL from environment variable
  const API_BASE_URL = process.env.PECANTV_API_URL || 'https://your-api-domain.com';
  
  try {
    // Forward the request to your Neon-hosted API
    const response = await axios({
      method: event.httpMethod,
      url: `${API_BASE_URL}${event.path}`,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': event.headers.authorization,
        ...event.headers
      },
      data: event.body ? JSON.parse(event.body) : undefined,
      params: event.queryStringParameters
    });

    return {
      statusCode: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      },
      body: JSON.stringify(response.data)
    };
  } catch (error) {
    return {
      statusCode: error.response?.status || 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        error: error.response?.data?.detail || 'Internal server error'
      })
    };
  }
};
```

**File: `netlify.toml`**
```toml
[build]
  functions = "netlify/functions"
  publish = "public"

[functions]
  directory = "netlify/functions"

[[headers]]
  for = "/api/*"
  [headers.values]
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Headers = "Content-Type, Authorization"
```

**Environment Variables in Netlify:**
```bash
# In Netlify Dashboard > Site settings > Environment variables
PECANTV_API_URL=https://your-neon-api-domain.com
```

#### Option 2: Webhook Integration

Create a webhook that triggers API calls to your Neon database:

**File: `netlify/functions/webhook-handler.js`**
```javascript
const axios = require('axios');

exports.handler = async (event, context) => {
  // Verify webhook secret (optional but recommended)
  const webhookSecret = process.env.WEBHOOK_SECRET;
  const signature = event.headers['x-webhook-signature'];
  
  if (webhookSecret && signature !== webhookSecret) {
    return {
      statusCode: 401,
      body: JSON.stringify({ error: 'Unauthorized' })
    };
  }

  const API_BASE_URL = process.env.PECANTV_API_URL;
  const payload = JSON.parse(event.body);

  try {
    // Example: Add content to database via webhook
    if (payload.action === 'add_content') {
      const response = await axios.post(`${API_BASE_URL}/content`, {
        title: payload.title,
        description: payload.description,
        type: payload.type,
        genre_id: payload.genre_id,
        rating_id: payload.rating_id,
        poster_url: payload.poster_url,
        trailer_url: payload.trailer_url,
        content_url: payload.content_url,
        runtime: payload.runtime
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.API_TOKEN}`
        }
      });

      return {
        statusCode: 200,
        body: JSON.stringify({
          success: true,
          content_id: response.data.id,
          message: 'Content added successfully'
        })
      };
    }

    // Example: Update user favorites via webhook
    if (payload.action === 'update_favorites') {
      const response = await axios.post(
        `${API_BASE_URL}/favorites/${payload.user_id}/toggle/${payload.content_id}`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${process.env.API_TOKEN}`
          }
        }
      );

      return {
        statusCode: 200,
        body: JSON.stringify({
          success: true,
          favorites: response.data
        })
      };
    }

    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Unknown action' })
    };

  } catch (error) {
    console.error('Webhook error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Webhook processing failed',
        details: error.response?.data || error.message
      })
    };
  }
};
```

#### Option 3: Serverless Function with Environment Variables

**File: `netlify/functions/database-query.js`**
```javascript
const { Pool } = require('pg');

exports.handler = async (event, context) => {
  // Get database connection from environment variables
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false
    }
  });

  try {
    const { query, params } = JSON.parse(event.body);
    
    const result = await pool.query(query, params);
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        success: true,
        data: result.rows,
        count: result.rowCount
      })
    };
  } catch (error) {
    console.error('Database error:', error);
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        error: 'Database query failed',
        details: error.message
      })
    };
  } finally {
    await pool.end();
  }
};
```

#### Environment Variables Setup

**In Netlify Dashboard:**
```bash
# Database connection
DATABASE_URL=postgresql://neondb_owner:password@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require

# API configuration
PECANTV_API_URL=https://your-api-domain.com
API_TOKEN=your_api_token_here

# Webhook security
WEBHOOK_SECRET=your_webhook_secret_here

# CORS settings
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

#### Testing the Integration

**Test API Proxy:**
```bash
curl -X GET "https://your-netlify-site.netlify.app/.netlify/functions/api-proxy/content" \
  -H "Content-Type: application/json"
```

**Test Webhook:**
```bash
curl -X POST "https://your-netlify-site.netlify.app/.netlify/functions/webhook-handler" \
  -H "Content-Type: application/json" \
  -H "x-webhook-signature: your_webhook_secret_here" \
  -d '{
    "action": "add_content",
    "title": "Test Movie",
    "description": "A test movie",
    "type": "FILM",
    "genre_id": 1,
    "rating_id": 1,
    "poster_url": "https://example.com/poster.jpg",
    "trailer_url": "https://example.com/trailer.mp4",
    "content_url": "https://example.com/movie.mp4",
    "runtime": 120
  }'
```

**Test Database Query:**
```bash
curl -X POST "https://your-netlify-site.netlify.app/.netlify/functions/database-query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM content WHERE type = $1 LIMIT 5",
    "params": ["SERIES"]
  }'
```

This setup allows you to:
- ✅ Call your Neon-hosted API from Netlify functions
- ✅ Process webhooks that interact with your database
- ✅ Execute direct database queries from serverless functions
- ✅ Maintain security with environment variables
- ✅ Handle CORS and authentication properly

## 🔧 Database Management

### URL Standardization

The project includes utilities for standardizing media URLs to Google Cloud Storage format:

```python
from api.url_utils import normalize_gcs_url

# Convert local paths to GCS URLs
gcs_url = normalize_gcs_url('dragnet/Dragnet1.mp4', 'dragnet')
# Returns: https://storage.googleapis.com/pecantv_series/dragnet/Dragnet1.mp4
```

### Maintenance Scripts

The `scripts/` directory contains various maintenance scripts:

- **URL Fixers**: Standardize episode and trailer URLs
- **Episode Management**: Add/update episode data
- **Series Verification**: Check data integrity
- **Content Loading**: Import from Wurl metadata files

### Quick Fix Script

Run the comprehensive fixer script to standardize all URLs:

```bash
python scripts/fix_all_urls.py
```

This script will:
- Fix episode content URLs
- Fix trailer URLs  
- Fix poster URLs
- Remove duplicate folder names
- Standardize to GCS format

## 📊 API Endpoints

### Content
- `GET /content` - Get all content with filtering
- `GET /content/{id}` - Get specific content
- `GET /content/{id}/episodes` - Get episodes for content

### Series
- `GET /series` - Get all series
- `GET /series/{id}/episodes` - Get episodes for series

### Episodes
- `GET /episodes` - Get all episodes
- `GET /episodes/{id}` - Get specific episode

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Favorites
- `GET /favorites/{user_id}` - Get user favorites
- `POST /favorites/{user_id}/toggle/{content_id}` - Toggle favorite

### Search & Filtering
- `GET /search?q={query}` - Search content
- `GET /genres` - Get all genres
- `GET /ratings` - Get all ratings

## 🗄️ Database Schema & DDL

### Database Overview
PecanTV uses PostgreSQL with the following key features:
- **UUID Support**: All tables have UUID primary keys for distributed systems
- **Backward Compatibility**: Integer IDs maintained for existing integrations
- **Automatic Timestamps**: `created_at` and `updated_at` fields with triggers
- **Foreign Key Constraints**: Referential integrity with CASCADE deletes
- **Indexes**: Optimized for common query patterns

### Complete DDL (Data Definition Language)

#### 1. Content Type Enum
```sql
CREATE TYPE content_type AS ENUM ('FILM', 'SERIES');
```

#### 2. Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_uuid ON users(uuid);
```

#### 3. Genres Table
```sql
CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_genres_name ON genres(name);
CREATE INDEX idx_genres_uuid ON genres(uuid);
```

#### 4. Ratings Table
```sql
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    code VARCHAR(10) NOT NULL UNIQUE, -- e.g., 'PG', 'PG-13', 'R'
    description TEXT,
    min_age INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_ratings_code ON ratings(code);
CREATE INDEX idx_ratings_uuid ON ratings(uuid);
```

#### 5. Content Table
```sql
CREATE TABLE content (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    poster_url TEXT NOT NULL,
    trailer_url TEXT NOT NULL,
    content_url TEXT NOT NULL,
    description TEXT,
    type content_type NOT NULL,
    runtime INTEGER NOT NULL,
    genre_id INTEGER REFERENCES genres(id),
    rating_id INTEGER REFERENCES ratings(id),
    release_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_content_type ON content(type);
CREATE INDEX idx_content_genre ON content(genre_id);
CREATE INDEX idx_content_rating ON content(rating_id);
CREATE INDEX idx_content_uuid ON content(uuid);
CREATE INDEX idx_content_title ON content(title);
```

#### 6. Episodes Table
```sql
CREATE TABLE episodes (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    season_number INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    runtime INTEGER,
    content_url TEXT NOT NULL,
    poster_url TEXT,
    series_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    content_uuid UUID REFERENCES content(uuid) ON DELETE CASCADE,
    air_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_episodes_series ON episodes(series_id);
CREATE INDEX idx_episodes_content_uuid ON episodes(content_uuid);
CREATE INDEX idx_episodes_season_episode ON episodes(series_id, season_number, episode_number);
CREATE INDEX idx_episodes_uuid ON episodes(uuid);
```

#### 7. Favorites Table
```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, content_id)
);

-- Indexes
CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_content ON favorites(content_id);
```

#### 8. Content-Genres Junction Table (Many-to-Many)
```sql
CREATE TABLE content_genres (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    content_uuid UUID REFERENCES content(uuid) ON DELETE CASCADE,
    genre_uuid UUID REFERENCES genres(uuid) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(content_id, genre_id)
);

-- Indexes
CREATE INDEX idx_content_genres_content ON content_genres(content_id);
CREATE INDEX idx_content_genres_genre ON content_genres(genre_id);
CREATE INDEX idx_content_genres_content_uuid ON content_genres(content_uuid);
CREATE INDEX idx_content_genres_genre_uuid ON content_genres(genre_uuid);
```

### Triggers and Functions

#### Automatic Timestamp Updates
```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for all tables
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_genres_updated_at
    BEFORE UPDATE ON genres
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ratings_updated_at
    BEFORE UPDATE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_updated_at
    BEFORE UPDATE ON content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_episodes_updated_at
    BEFORE UPDATE ON episodes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Data Keys and Relationships

#### Primary Keys
- **users**: `id` (SERIAL), `uuid` (UUID)
- **genres**: `id` (SERIAL), `uuid` (UUID)
- **ratings**: `id` (SERIAL), `uuid` (UUID)
- **content**: `id` (SERIAL), `uuid` (UUID)
- **episodes**: `id` (SERIAL), `uuid` (UUID)
- **favorites**: `id` (SERIAL)
- **content_genres**: `id` (SERIAL)

#### Foreign Keys
- **content.genre_id** → **genres.id**
- **content.rating_id** → **ratings.id**
- **episodes.series_id** → **content.id**
- **episodes.content_uuid** → **content.uuid**
- **favorites.user_id** → **users.id**
- **favorites.content_id** → **content.id**
- **content_genres.content_id** → **content.id**
- **content_genres.genre_id** → **genres.id**
- **content_genres.content_uuid** → **content.uuid**
- **content_genres.genre_uuid** → **genres.uuid**

#### Unique Constraints
- **users.email**: Unique email addresses
- **users.uuid**: Unique UUID
- **genres.name**: Unique genre names
- **genres.uuid**: Unique UUID
- **ratings.code**: Unique rating codes
- **ratings.uuid**: Unique UUID
- **content.uuid**: Unique UUID
- **episodes.uuid**: Unique UUID
- **favorites**: Composite unique on (user_id, content_id)
- **content_genres**: Composite unique on (content_id, genre_id)

### Common Queries

#### Get All Content with Genre and Rating
```sql
SELECT 
    c.id,
    c.title,
    c.description,
    c.type,
    c.runtime,
    g.name as genre,
    r.code as rating,
    c.release_date
FROM content c
LEFT JOIN genres g ON c.genre_id = g.id
LEFT JOIN ratings r ON c.rating_id = r.id
ORDER BY c.title;
```

#### Get Series with Episode Count
```sql
SELECT 
    c.id,
    c.title,
    COUNT(e.id) as episode_count
FROM content c
LEFT JOIN episodes e ON c.id = e.series_id
WHERE c.type = 'SERIES'
GROUP BY c.id, c.title
ORDER BY c.title;
```

#### Get User Favorites
```sql
SELECT 
    c.title,
    c.description,
    c.type,
    f.created_at as favorited_at
FROM favorites f
JOIN content c ON f.content_id = c.id
WHERE f.user_id = $1
ORDER BY f.created_at DESC;
```

#### Get Episodes for a Series
```sql
SELECT 
    e.season_number,
    e.episode_number,
    e.title,
    e.description,
    e.runtime,
    e.content_url
FROM episodes e
WHERE e.series_id = $1
ORDER BY e.season_number, e.episode_number;
```

### Database Migration Scripts

The project includes migration scripts for schema updates:

- **`database/schema.sql`**: Initial schema creation
- **`database/migration_multiple_genres.sql`**: Many-to-many genre relationships
- **`database_exports/`**: Database dumps for backup and restoration

### Data Import/Export

#### Export Database
```bash
# Full database dump
pg_dump -h your-host -U your-user -d your-database > backup.sql

# Data only
pg_dump -h your-host -U your-user -d your-database --data-only > data_backup.sql

# Schema only
pg_dump -h your-host -U your-user -d your-database --schema-only > schema_backup.sql
```

#### Import Database
```bash
# Restore from backup
psql -h your-host -U your-user -d your-database < backup.sql
```

### Performance Optimization

#### Recommended Indexes
```sql
-- For content searches
CREATE INDEX idx_content_title_lower ON content(LOWER(title));
CREATE INDEX idx_content_type_runtime ON content(type, runtime);

-- For episode queries
CREATE INDEX idx_episodes_series_season_episode ON episodes(series_id, season_number, episode_number);

-- For user favorites
CREATE INDEX idx_favorites_user_created ON favorites(user_id, created_at DESC);
```

#### Query Optimization Tips
1. Use UUID indexes for distributed systems
2. Include `created_at` in composite indexes for time-based queries
3. Use partial indexes for filtered queries
4. Monitor query performance with `EXPLAIN ANALYZE`

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration for cross-origin requests
- Environment variable management for secrets

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions to:
- Render (recommended)
- Railway
- Vercel

## 🛠️ Development

### Adding New Content

1. Add media files to `pecantv_series/` directory
2. Use maintenance scripts to import metadata
3. Verify URLs are properly formatted
4. Test playback in iOS app

### Database Migrations

The project uses SQLAlchemy for database management. Schema changes should be handled through:
- Model updates in `models.py`
- Migration scripts in `scripts/`
- Data verification scripts

### URL Standards

All media URLs should follow the GCS format:
```
https://storage.googleapis.com/pecantv_series/{series_folder}/{filename}
```

## 📝 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   pkill -f "python main.py"
   ```

2. **Database Connection Issues**
   - Verify environment variables
   - Check Neon database status
   - Test connection with `test_db.py`

3. **Media Playback Issues**
   - Verify URLs are in GCS format
   - Check file permissions
   - Run URL fixer scripts

4. **iOS App Connection**
   - Update API base URL
   - Check CORS configuration
   - Verify network connectivity

### Debug Commands

```bash
# Test database connection
python api/test_db.py

# Check API health
curl http://localhost:8000/health

# Verify episode URLs
python scripts/check_episode_urls.py

# Fix all URLs
python scripts/fix_all_urls.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For technical support or questions:
- Check the troubleshooting section
- Review the maintenance scripts
- Test with the provided debug commands

## 🗄️ Database: Neon (PostgreSQL)

PecanTV uses [Neon](https://neon.tech/) for managed PostgreSQL hosting. You can access and manage your database directly from the Neon dashboard.

### How to Access and Use Neon from the Dashboard

1. **Log in to Neon**
   - Go to [https://console.neon.tech/](https://console.neon.tech/) and log in with your account.

2. **Select Your Project**
   - Click on your PecanTV project to open the project dashboard.

3. **Find Connection Details**
   - In the dashboard, go to the **Connection Details** section.
   - You will see a connection string like:
     ```
     postgresql://<user>:<password>@<host>/<database>?sslmode=require
     ```
   - Example:
     ```
     postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
     ```

4. **Copy the Connection String**
   - Use the copy button to copy the full connection string.

5. **Set Environment Variable**
   - In your local environment, set the `DATABASE_URL` environment variable to this value. For example:
     ```bash
     export DATABASE_URL="postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"
     ```
   - You can also add this to a `.env` file in the `api/` directory:
     ```
     DATABASE_URL=postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
     ```

6. **Use in Your Application**
   - The FastAPI backend will automatically use this environment variable for database connections.

7. **Query and Manage Data**
   - From the Neon dashboard, you can:
     - Run SQL queries directly in the web console
     - View tables, rows, and schema
     - Manage users and roles
     - Monitor database activity and performance

8. **Resetting or Migrating Data**
   - You can reset your database or create branches for testing from the dashboard.
   - Always back up important data before making destructive changes.

--- 