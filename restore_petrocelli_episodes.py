#!/usr/bin/env python3
"""
Restore all Petrocelli episodes (22 total) into the local database.
"""

import psycopg2
from datetime import datetime, timezone

DB_PARAMS = {
    'host': 'localhost',
    'port': 5433,
    'database': 'pecantv',
    'user': 'postgres',
    'password': 'postgres'
}

# Petrocelli episode mapping (add more if you have all 22 filenames)
PETROCELLI_EPISODES = [
    (1, "Deadly Journey", "Petrocelli-Deadly-Journey_2p-1080-wCredits.mp4"),
    (2, "Face of Evil", "Petrocelli-Face-of-Evil_2p-1080-wCredits.mp4"),
    (3, "Four the Hard Way", "Petrocelli-Four-the-Hard-Way_2p-1080-wCredits.mp4"),
    (4, "Shadow of Fear", "Petrocelli-Shadow-of-Fear_2p-1080-wCredits.mp4"),
    (5, "The Night Visitor", "Petrocelli-The-Night-Visitor_2p-1080-wCredits.mp4"),
    (6, "Too Many Alibis", "Petrocelli-Too-Many-Alibis_2p-1080-wCredits.mp4"),
    (7, "Shadow of a Doubt", "Petrocelli-Shadow-of-a-Doubt_2p-1080-wCredits.mp4"),
    (8, "Survival", "Petrocelli-Survival_2p-1080-wCredits.mp4"),
    (9, "Death in Small Doses", "Petrocelli-Death-in-Small-Doses_2p-1080-wCredits.mp4"),
    (10, "Once Upon a Victim", "Petrocelli-Once-Upon-a-Victim_2p-1080-wCredits.mp4"),
    (11, "Counterploy", "Petrocelli-Counterploy_2p-1080-wCredits.mp4"),
    (12, "By Reason of Madness", "Petrocelli-By-Reason-of-Madness_2p-1080-wCredits.mp4"),
    (13, "A Fallen Idol", "Petrocelli-A-Fallen-Idol_2p-1080-wCredits.mp4"),
    # Add more episodes here if you have them (up to 22)
]

SERIES_ID = 21  # Petrocelli series_id in content table

POSTER_URL = "pecantv_series/petrocelli/Petrocelli1_poster.jpg"


def restore_petrocelli_episodes():
    print("🔄 Restoring Petrocelli episodes...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Remove any existing Petrocelli episodes
        cur.execute("DELETE FROM episodes WHERE series_id = %s", (SERIES_ID,))
        print("🧹 Removed existing Petrocelli episodes.")

        inserted = 0
        for ep_num, title, filename in PETROCELLI_EPISODES:
            content_url = f"https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/{filename}"
            description = f"Petrocelli S1E{ep_num}: {title}"
            runtime = 48  # Placeholder runtime
            air_date = None  # Set if you have it
            now = datetime.now(timezone.utc)

            cur.execute(
                """
                INSERT INTO episodes (
                    series_id, season_number, episode_number, title, description, content_url, thumbnail_url, runtime, air_date, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (SERIES_ID, 1, ep_num, title, description, content_url, POSTER_URL, runtime, air_date, now, now)
            )
            print(f"  ✅ Inserted S1E{ep_num}: {title}")
            inserted += 1

        conn.commit()
        print(f"\n🎉 Restored {inserted} Petrocelli episodes!")

        # Show summary
        cur.execute("SELECT episode_number, title FROM episodes WHERE series_id = %s ORDER BY episode_number", (SERIES_ID,))
        episodes = cur.fetchall()
        print("\nCurrent Petrocelli episodes in DB:")
        for ep_num, title in episodes:
            print(f"  S1E{ep_num}: {title}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    restore_petrocelli_episodes() 