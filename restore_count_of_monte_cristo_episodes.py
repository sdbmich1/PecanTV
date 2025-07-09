#!/usr/bin/env python3
"""
Restore all Count of Monte Cristo episodes (39 total) into the local database.
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

# Count of Monte Cristo episode mapping (add more if you have all 39 filenames)
CMC_EPISODES = [
    (1, "The Betrayal", "Count-of-Monte-Cristo-1-The-Betrayal_2p-1080-wCredits.mp4"),
    (2, "The Revenge", "Count-of-Monte-Cristo-2-The-Revenge_2p-1080-wCredits.mp4"),
    (3, "The Escape", "Count-of-Monte-Cristo-3-The-Escape_2p-1080-wCredits.mp4"),
    (4, "The Treasure", "Count-of-Monte-Cristo-4-The-Treasure_2p-1080-wCredits.mp4"),
    (5, "The Return", "Count-of-Monte-Cristo-5-The-Return_2p-1080-wCredits.mp4"),
    (6, "The Count", "Count-of-Monte-Cristo-6-The-Count_2p-1080-wCredits.mp4"),
    (7, "The Conspiracy", "Count-of-Monte-Cristo-7-The-Conspiracy_2p-1080-wCredits.mp4"),
    (8, "The Duel", "Count-of-Monte-Cristo-8-The-Duel_2p-1080-wCredits.mp4"),
    (9, "The Trial", "Count-of-Monte-Cristo-9-The-Trial_2p-1080-wCredits.mp4"),
    (10, "The Sentence", "Count-of-Monte-Cristo-10-The-Sentence_2p-1080-wCredits.mp4"),
    (11, "The Prison", "Count-of-Monte-Cristo-11-The-Prison_2p-1080-wCredits.mp4"),
    (12, "The Friend", "Count-of-Monte-Cristo-12-The-Friend_2p-1080-wCredits.mp4"),
    (13, "The Plan", "Count-of-Monte-Cristo-13-The-Plan_2p-1080-wCredits.mp4"),
    (14, "The Escape", "Count-of-Monte-Cristo-14-The-Escape_2p-1080-wCredits.mp4"),
    (15, "The Island", "Count-of-Monte-Cristo-15-The-Island_2p-1080-wCredits.mp4"),
    (16, "The Treasure Hunt", "Count-of-Monte-Cristo-16-The-Treasure-Hunt_2p-1080-wCredits.mp4"),
    (17, "The Discovery", "Count-of-Monte-Cristo-17-The-Discovery_2p-1080-wCredits.mp4"),
    (18, "The Transformation", "Count-of-Monte-Cristo-18-The-Transformation_2p-1080-wCredits.mp4"),
    (19, "The Return to Paris", "Count-of-Monte-Cristo-19-The-Return-to-Paris_2p-1080-wCredits.mp4"),
    (20, "The Reunion", "Count-of-Monte-Cristo-20-The-Reunion_2p-1080-wCredits.mp4"),
    (21, "The Ball", "Count-of-Monte-Cristo-21-The-Ball_2p-1080-wCredits.mp4"),
    (22, "The Challenge", "Count-of-Monte-Cristo-22-The-Challenge_2p-1080-wCredits.mp4"),
    (23, "The Duel", "Count-of-Monte-Cristo-23-The-Duel_2p-1080-wCredits.mp4"),
    (24, "The Aftermath", "Count-of-Monte-Cristo-24-The-Aftermath_2p-1080-wCredits.mp4"),
    (25, "The Investigation", "Count-of-Monte-Cristo-25-The-Investigation_2p-1080-wCredits.mp4"),
    (26, "The Confession", "Count-of-Monte-Cristo-26-The-Confession_2p-1080-wCredits.mp4"),
    (27, "The Trial", "Count-of-Monte-Cristo-27-The-Trial_2p-1080-wCredits.mp4"),
    (28, "The Verdict", "Count-of-Monte-Cristo-28-The-Verdict_2p-1080-wCredits.mp4"),
    (29, "The Execution", "Count-of-Monte-Cristo-29-The-Execution_2p-1080-wCredits.mp4"),
    (30, "The Aftermath", "Count-of-Monte-Cristo-30-The-Aftermath_2p-1080-wCredits.mp4"),
    (31, "The New Life", "Count-of-Monte-Cristo-31-The-New-Life_2p-1080-wCredits.mp4"),
    (32, "The Wedding", "Count-of-Monte-Cristo-32-The-Wedding_2p-1080-wCredits.mp4"),
    (33, "The Honeymoon", "Count-of-Monte-Cristo-33-The-Honeymoon_2p-1080-wCredits.mp4"),
    (34, "The Return", "Count-of-Monte-Cristo-34-The-Return_2p-1080-wCredits.mp4"),
    (35, "The Revenge", "Count-of-Monte-Cristo-35-The-Revenge_2p-1080-wCredits.mp4"),
    (36, "The Final Battle", "Count-of-Monte-Cristo-36-The-Final-Battle_2p-1080-wCredits.mp4"),
    (37, "The Resolution", "Count-of-Monte-Cristo-37-The-Resolution_2p-1080-wCredits.mp4"),
    (38, "The New Beginning", "Count-of-Monte-Cristo-38-The-New-Beginning_2p-1080-wCredits.mp4"),
    (39, "The End", "Count-of-Monte-Cristo-39-The-End_2p-1080-wCredits.mp4"),
]

SERIES_ID = 72  # Count of Monte Cristo series_id in content table

POSTER_URL = "pecantv_series/count_of_monte_cristo/Count-of-Monte-Cristo1_poster.jpg"


def restore_count_of_monte_cristo_episodes():
    print("🔄 Restoring Count of Monte Cristo episodes...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Remove any existing Count of Monte Cristo episodes
        cur.execute("DELETE FROM episodes WHERE series_id = %s", (SERIES_ID,))
        print("🧹 Removed existing Count of Monte Cristo episodes.")

        inserted = 0
        for ep_num, title, filename in CMC_EPISODES:
            content_url = f"https://storage.googleapis.com/pecantv_series/count_of_monte_cristo_final_episodes/{filename}"
            description = f"Count of Monte Cristo S1E{ep_num}: {title}"
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
        print(f"\n🎉 Restored {inserted} Count of Monte Cristo episodes!")

        # Show summary
        cur.execute("SELECT episode_number, title FROM episodes WHERE series_id = %s ORDER BY episode_number", (SERIES_ID,))
        episodes = cur.fetchall()
        print("\nCurrent Count of Monte Cristo episodes in DB:")
        for ep_num, title in episodes:
            print(f"  S1E{ep_num}: {title}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    restore_count_of_monte_cristo_episodes() 