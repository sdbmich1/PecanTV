#!/usr/bin/env python3
"""
Update all Petrocelli episode content_urls to use the new GCS folder.
"""
import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import models

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not set in .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

NEW_BASE = "https://storage.googleapis.com/pecantv_series/petrocelli_final_episodes/"

# Find all Petrocelli episodes
petrocelli_episodes = session.query(models.Episode).filter(models.Episode.series_name.ilike("petrocelli%"))

updated = 0
for ep in petrocelli_episodes:
    # Extract the filename from the old URL or title
    # Try to use the filename from the old content_url if present
    filename = None
    if ep.content_url and ep.content_url.startswith("http"):
        filename = os.path.basename(ep.content_url)
    else:
        # Fallback: try to construct from title
        safe_title = ep.title.replace(" ", "-").replace("'", "").replace(",", "").replace("/", "-")
        filename = f"Petrocelli-{safe_title}.mp4"
    new_url = NEW_BASE + filename
    if ep.content_url != new_url:
        print(f"Updating episode {ep.id} ({ep.title}):\n  {ep.content_url} ->\n  {new_url}")
        ep.content_url = new_url
        updated += 1

session.commit()
print(f"✅ Updated {updated} Petrocelli episode content_urls.")
session.close() 