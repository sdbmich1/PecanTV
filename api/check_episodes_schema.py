#!/usr/bin/env python3
"""
Check the episodes table schema
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import engine
from sqlalchemy import text

def check_episodes_schema():
    """Check the episodes table schema"""
    
    with engine.connect() as conn:
        print("🔍 Checking episodes table schema...")
        print("=" * 40)
        
        # Get table schema
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'episodes'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print("Episodes table columns:")
        for col_name, data_type, is_nullable, col_default in columns:
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default = f" DEFAULT {col_default}" if col_default else ""
            print(f"  {col_name}: {data_type} {nullable}{default}")
        
        # Check a sample episode to see what values are used
        print("\n📋 Sample episode data:")
        result = conn.execute(text("""
            SELECT * FROM episodes LIMIT 1
        """))
        
        if result.rowcount > 0:
            sample = result.fetchone()
            print(f"Sample episode: {sample}")

if __name__ == "__main__":
    check_episodes_schema() 