#!/usr/bin/env python3
"""
Add series entries back to content table
"""

import os
import uuid
from sqlalchemy import create_engine, text
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def main():
    print("🔧 Adding series entries back to content table...")
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Define series to add
        series_to_add = [
            {
                'id': 49,
                'title': 'Longstreet',
                'type': 'SERIES',
                'poster_url': 'https://storage.googleapis.com/pecantv_series/default_poster.jpg',
                'trailer_url': 'https://storage.googleapis.com/pecantv_series/default_trailer.mp4',
                'content_url': 'https://storage.googleapis.com/pecantv_series/default_content.mp4',
                'description': 'Longstreet series'
            },
            {
                'id': 62,
                'title': 'Ghost Squad',
                'type': 'SERIES',
                'poster_url': 'https://storage.googleapis.com/pecantv_series/default_poster.jpg',
                'trailer_url': 'https://storage.googleapis.com/pecantv_series/default_trailer.mp4',
                'content_url': 'https://storage.googleapis.com/pecantv_series/default_content.mp4',
                'description': 'Ghost Squad series'
            },
            {
                'id': 78,
                'title': 'Bonanza',
                'type': 'SERIES',
                'poster_url': 'https://storage.googleapis.com/pecantv_series/default_poster.jpg',
                'trailer_url': 'https://storage.googleapis.com/pecantv_series/default_trailer.mp4',
                'content_url': 'https://storage.googleapis.com/pecantv_series/default_content.mp4',
                'description': 'Bonanza series'
            }
        ]
        
        # Add each series
        for series in series_to_add:
            try:
                conn.execute(text("""
                    INSERT INTO content (
                        id, title, type, poster_url, trailer_url, content_url, description, runtime,
                        created_at, updated_at, uuid
                    ) VALUES (
                        :id, :title, :type, :poster_url, :trailer_url, :content_url, :description, :runtime,
                        :created_at, :updated_at, :uuid
                    )
                """), {
                    'id': series['id'],
                    'title': series['title'],
                    'type': series['type'],
                    'poster_url': series['poster_url'],
                    'trailer_url': series['trailer_url'],
                    'content_url': series['content_url'],
                    'description': series['description'],
                    'runtime': 0,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow(),
                    'uuid': str(uuid.uuid4())
                })
                
                print(f"✅ Added {series['title']} to content table")
                
            except Exception as e:
                print(f"❌ Error adding {series['title']}: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ All series entries added successfully!")
        
        # Verify the episodes are now accessible
        print(f"\n🔍 Verifying episodes:")
        series_names = {49: 'Longstreet', 62: 'Ghost Squad', 78: 'Bonanza'}
        
        for series_id, series_name in series_names.items():
            result = conn.execute(text("""
                SELECT COUNT(*) FROM episodes WHERE series_id = :series_id
            """), {'series_id': series_id})
            
            count = result.fetchone()[0]
            print(f"   📺 {series_name}: {count} episodes")

if __name__ == "__main__":
    main() 