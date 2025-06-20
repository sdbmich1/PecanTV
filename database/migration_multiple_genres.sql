-- Migration to support multiple genres per content item
-- This creates a many-to-many relationship between content and genres

-- Create the junction table for content-genre relationships
CREATE TABLE content_genres (
    id SERIAL PRIMARY KEY,
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(content_id, genre_id)
);

-- Create index for better query performance
CREATE INDEX idx_content_genres_content_id ON content_genres(content_id);
CREATE INDEX idx_content_genres_genre_id ON content_genres(genre_id);

-- Migrate existing data from content.genre_id to content_genres junction table
INSERT INTO content_genres (content_id, genre_id)
SELECT id, genre_id 
FROM content 
WHERE genre_id IS NOT NULL
ON CONFLICT (content_id, genre_id) DO NOTHING;

-- Add a trigger to update the junction table when content is updated
CREATE OR REPLACE FUNCTION update_content_genres()
RETURNS TRIGGER AS $$
BEGIN
    -- Remove old genre relationships
    DELETE FROM content_genres WHERE content_id = NEW.id;
    
    -- Add new genre relationship if genre_id is set
    IF NEW.genre_id IS NOT NULL THEN
        INSERT INTO content_genres (content_id, genre_id) 
        VALUES (NEW.id, NEW.genre_id)
        ON CONFLICT (content_id, genre_id) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_content_genres_trigger
    AFTER UPDATE ON content
    FOR EACH ROW
    EXECUTE FUNCTION update_content_genres();

-- Create a function to get genres for a content item
CREATE OR REPLACE FUNCTION get_content_genres(content_id_param INTEGER)
RETURNS TABLE(genre_id INTEGER, genre_name VARCHAR(50)) AS $$
BEGIN
    RETURN QUERY
    SELECT g.id, g.name
    FROM genres g
    JOIN content_genres cg ON g.id = cg.genre_id
    WHERE cg.content_id = content_id_param;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get content by genre
CREATE OR REPLACE FUNCTION get_content_by_genre(genre_name_param VARCHAR(50))
RETURNS TABLE(
    id INTEGER,
    title VARCHAR(255),
    poster_url TEXT,
    trailer_url TEXT,
    content_url TEXT,
    description TEXT,
    type content_type,
    runtime INTEGER,
    rating_id INTEGER,
    release_date DATE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT c.id, c.title, c.poster_url, c.trailer_url, c.content_url, 
           c.description, c.type, c.runtime, c.rating_id, c.release_date, 
           c.created_at, c.updated_at
    FROM content c
    JOIN content_genres cg ON c.id = cg.content_id
    JOIN genres g ON cg.genre_id = g.id
    WHERE LOWER(g.name) = LOWER(genre_name_param);
END;
$$ LANGUAGE plpgsql; 