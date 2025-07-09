import psycopg2
import uuid

DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

conn = psycopg2.connect(**DB_PARAMS)
cur = conn.cursor()

# Get Bonanza series id and uuid
cur.execute('SELECT id, uuid FROM content WHERE title = %s AND type = %s', ('Bonanza', 'SERIES'))
bonanza = cur.fetchone()
if not bonanza:
    print('Bonanza series not found!')
    exit(1)
bonanza_id, bonanza_uuid = bonanza

# Get The Savage from content table
cur.execute('SELECT id, title, content_url, poster_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at, uuid FROM content WHERE title = %s', ('The Savage',))
ep = cur.fetchone()
if not ep:
    print('The Savage not found!')
    exit(1)
content_id, title, content_url, poster_url, description, runtime, genre_id, rating_id, release_date, created_at, updated_at, content_uuid = ep

# Find next episode number for Bonanza
cur.execute('SELECT MAX(episode_number) FROM episodes WHERE series_id = %s AND season_number = 1', (bonanza_id,))
max_episode = cur.fetchone()[0] or 0
episode_number = max_episode + 1

# Insert into episodes table
episode_uuid = str(uuid.uuid4())
cur.execute('''INSERT INTO episodes (uuid, title, description, season_number, episode_number, runtime, content_url, poster_url, series_id, content_uuid, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (episode_uuid, title, description, 1, episode_number, runtime, content_url, poster_url, bonanza_id, content_uuid, created_at, updated_at))

# Delete from content table
cur.execute('DELETE FROM content WHERE id = %s', (content_id,))

conn.commit()
print(f"Moved '{title}' to Bonanza episodes as E{episode_number} and removed from films.")
cur.close()
conn.close() 