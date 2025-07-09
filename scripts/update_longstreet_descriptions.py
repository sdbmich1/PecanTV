#!/usr/bin/env python3
"""
Update Longstreet episode descriptions in the database using Wurl metadata.
"""
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

EXCEL_PATH = '../Wurl - File Upload Metadata_Version 7.0.40.xlsx'
SERIES_ID = 49  # Longstreet

# Load Longstreet episode metadata
print(f"Loading metadata from {EXCEL_PATH}")
df = pd.read_excel(EXCEL_PATH)
ls = df[df['Series Name'].astype(str).str.contains('Longstreet', case=False, na=False)]

# Map episode number to description
epi_map = {}
for _, row in ls.iterrows():
    try:
        ep_num = int(row['Episode Number'])
    except Exception:
        continue
    desc = str(row['Description']) if row['Description'] else ''
    title = str(row['Title']) if row['Title'] else ''
    epi_map[ep_num] = {'description': desc, 'title': title}

print(f"Found {len(epi_map)} Longstreet episodes in metadata.")

# Update the database
def update_longstreet_descriptions():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    updated = 0
    for ep_num, data in epi_map.items():
        cur.execute("""
            UPDATE episodes
            SET description = %s, title = %s
            WHERE series_id = %s AND episode_number = %s
        """, (data['description'], data['title'], SERIES_ID, ep_num))
        if cur.rowcount:
            print(f"Updated episode {ep_num}: {data['title']}")
            updated += 1
    conn.commit()
    print(f"\n✅ Updated {updated} Longstreet episodes with descriptions.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    update_longstreet_descriptions() 