#!/usr/bin/env python3
import os
import sys
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

# Load environment variables
load_dotenv()

def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
    if "neon.tech" in database_url:
        parsed = urllib.parse.urlparse(database_url)
        if parsed.scheme == "postgresql":
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
    return database_url

def print_db_schema():
    engine = create_engine(get_database_url())
    inspector = inspect(engine)
    print("\nDatabase Tables and Columns:")
    for table_name in inspector.get_table_names():
        print(f"\nTable: {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"  - {column['name']} ({column['type']})")

if __name__ == "__main__":
    print_db_schema() 