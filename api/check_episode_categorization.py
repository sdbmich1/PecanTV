import psycopg2

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
cur.execute('SELECT title, episode_number, series_id FROM episodes WHERE title IN (%s, %s, %s) ORDER BY series_id, episode_number', (
    'Please Leave the Wreck for Others to Enjoy',
    'Mecklenburg',
    'Lichtenburg',
))
results = cur.fetchall()
for title, episode_num, series_id in results:
    series = {49: 'Longstreet', 72: 'Count of Monte Cristo', 700: 'Man with a Camera'}.get(series_id, str(series_id))
    print(f'{title} (E{episode_num}, series: {series})')
cur.close()
conn.close() 