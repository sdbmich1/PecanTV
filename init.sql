-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Movies/Shows table
CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_date DATE,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posters table (one-to-many with movies)
CREATE TABLE IF NOT EXISTS posters (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Video files table (one-to-many with movies)
CREATE TABLE IF NOT EXISTS video_files (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    quality VARCHAR(50),
    transcoded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 