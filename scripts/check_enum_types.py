#!/usr/bin/env python3
"""
Script to check enum types in the Neon database.
"""

import psycopg2

# Database connection parameters for Neon
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def check_enum_types():
    """Check what enum types exist in the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🔍 Checking enum types in database")
        print("=" * 50)
        
        # Check all enum types
        cur.execute("""
            SELECT t.typname, e.enumlabel
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            ORDER BY t.typname, e.enumsortorder;
        """)
        
        enum_types = {}
        for enum_name, enum_value in cur.fetchall():
            if enum_name not in enum_types:
                enum_types[enum_name] = []
            enum_types[enum_name].append(enum_value)
        
        print("📋 Enum types found:")
        for enum_name, values in enum_types.items():
            print(f"   {enum_name}: {values}")
        
        # Check the content table structure
        print("\n🔍 Content table structure:")
        cur.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'content' AND column_name = 'type';
        """)
        
        column_info = cur.fetchone()
        if column_info:
            column_name, data_type, udt_name = column_info
            print(f"   Column: {column_name}")
            print(f"   Data Type: {data_type}")
            print(f"   UDT Name: {udt_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_enum_types() 