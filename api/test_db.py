#!/usr/bin/env python3
"""
Test database connection
"""

import os
from sqlalchemy import create_engine, text

# Test the connection string directly
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

print(f"Testing connection string: {DATABASE_URL}")

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    print("✅ Engine created successfully")
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()
        print(f"✅ Connected successfully! PostgreSQL version: {version[0]}")
        
        # Test a simple query
        result = conn.execute(text("SELECT COUNT(*) FROM content"))
        count = result.fetchone()
        print(f"✅ Content table has {count[0]} rows")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}") 