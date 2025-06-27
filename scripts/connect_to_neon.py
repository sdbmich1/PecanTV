#!/usr/bin/env python3
"""
Neon Database Explorer Script
Connect to your Neon database and explore the data.
"""

import psycopg2
import pandas as pd
from tabulate import tabulate
import sys

# Your Neon connection string
NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_K1HJErMqmX8g@ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require"

def connect_to_neon():
    """Connect to Neon database."""
    try:
        conn = psycopg2.connect(NEON_CONNECTION_STRING)
        print("✅ Connected to Neon database successfully!")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None

def list_tables(conn):
    """List all tables in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
    print("\n📋 Tables in your database:")
    for table in tables:
        print(f"  - {table[0]}")
    return [table[0] for table in tables]

def show_table_info(conn, table_name):
    """Show information about a specific table."""
    with conn.cursor() as cur:
        # Get column information
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cur.fetchone()[0]
        
    print(f"\n📊 Table: {table_name}")
    print(f"   Rows: {row_count}")
    print("\n   Columns:")
    for col in columns:
        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
        print(f"     - {col[0]} ({col[1]}) {nullable}")

def show_sample_data(conn, table_name, limit=5):
    """Show sample data from a table."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
            rows = cur.fetchall()
            
            if not rows:
                print(f"   No data found in {table_name}")
                return
            
            # Get column names
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position;")
            columns = [col[0] for col in cur.fetchall()]
            
            # Create DataFrame for nice display
            df = pd.DataFrame(rows, columns=columns)
            print(f"\n   Sample data (first {limit} rows):")
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
            
    except Exception as e:
        print(f"   Error reading data: {e}")

def run_custom_query(conn, query):
    """Run a custom SQL query."""
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            
            if not rows:
                print("   No results found.")
                return
            
            # Get column names
            columns = [desc[0] for desc in cur.description]
            
            # Create DataFrame for nice display
            df = pd.DataFrame(rows, columns=columns)
            print(f"\n   Query results:")
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
            
    except Exception as e:
        print(f"   Error executing query: {e}")

def main():
    print("🔍 Neon Database Explorer")
    print("=" * 50)
    
    # Connect to database
    conn = connect_to_neon()
    if not conn:
        return
    
    try:
        # List tables
        tables = list_tables(conn)
        
        if not tables:
            print("No tables found in the database.")
            return
        
        # Show info for each table
        for table in tables:
            show_table_info(conn, table)
            show_sample_data(conn, table)
        
        # Interactive mode
        print("\n" + "=" * 50)
        print("🔧 Interactive Mode")
        print("Enter SQL queries to explore your data (type 'quit' to exit):")
        
        while True:
            try:
                query = input("\nSQL> ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                if query:
                    run_custom_query(conn, query)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    finally:
        conn.close()
        print("\n👋 Disconnected from Neon database.")

if __name__ == "__main__":
    main() 