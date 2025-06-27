#!/usr/bin/env python3
"""
Script to search for all Petrocelli-related data across all tables in the database.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def search_all_petrocelli_data():
    """Search for all Petrocelli-related data across all tables."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Searching for all Petrocelli-related data across all tables...")
        print("=" * 70)
        
        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        
        for table in tables:
            table_name = table['table_name']
            print(f"\n📋 Checking table: {table_name}")
            
            # Get column names for this table
            cur.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            column_names = [col['column_name'] for col in columns]
            
            # Search for Petrocelli in text/varchar columns
            for col in columns:
                if col['data_type'] in ['text', 'character varying', 'varchar']:
                    try:
                        cur.execute(f"""
                            SELECT COUNT(*) as count 
                            FROM {table_name} 
                            WHERE {col['column_name']} ILIKE '%petrocelli%'
                        """)
                        result = cur.fetchone()
                        if result['count'] > 0:
                            print(f"  ✅ Found {result['count']} records with 'petrocelli' in {col['column_name']}")
                            
                            # Show sample data
                            cur.execute(f"""
                                SELECT {col['column_name']} 
                                FROM {table_name} 
                                WHERE {col['column_name']} ILIKE '%petrocelli%'
                                LIMIT 3
                            """)
                            samples = cur.fetchall()
                            for sample in samples:
                                value = sample[col['column_name']]
                                if value:
                                    print(f"    Sample: {value[:100]}...")
                    except Exception as e:
                        # Skip if column doesn't support ILIKE or other issues
                        pass
        
        # Also check for any JSON or JSONB columns that might contain Petrocelli data
        print("\n" + "=" * 70)
        print("🔍 Checking for JSON columns that might contain Petrocelli data...")
        
        for table in tables:
            table_name = table['table_name']
            
            # Check for JSON columns
            cur.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                AND data_type IN ('json', 'jsonb')
            """)
            
            json_columns = cur.fetchall()
            for col in json_columns:
                try:
                    cur.execute(f"""
                        SELECT COUNT(*) as count 
                        FROM {table_name} 
                        WHERE {col['column_name']}::text ILIKE '%petrocelli%'
                    """)
                    result = cur.fetchone()
                    if result['count'] > 0:
                        print(f"  ✅ Found {result['count']} records with 'petrocelli' in JSON column {table_name}.{col['column_name']}")
                except Exception as e:
                    pass
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    search_all_petrocelli_data() 