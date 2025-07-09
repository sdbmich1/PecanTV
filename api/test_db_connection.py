#!/usr/bin/env python3
"""
Script to test database connection and identify issues
"""

import psycopg2
import sys

def main():
    print("Testing database connection...")
    
    try:
        # Database connection
        conn = psycopg2.connect(
            host='localhost',
            database='pecantv',
            user='postgres',
            password='postgres',
            port='5433'
        )
        
        print("✅ Database connection successful")
        
        cursor = conn.cursor()
        print("✅ Cursor created successfully")
        
        # Test a simple query
        cursor.execute("SELECT COUNT(*) FROM content")
        result = cursor.fetchone()
        print(f"✅ Query successful: {result[0]} content items in database")
        
        # Test a more complex query
        cursor.execute("SELECT id, title FROM content LIMIT 3")
        results = cursor.fetchall()
        print(f"✅ Complex query successful: {len(results)} results")
        for row in results:
            print(f"  ID: {row[0]}, Title: '{row[1]}'")
        
        # Close everything properly
        cursor.close()
        conn.close()
        print("✅ Connection closed successfully")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return 1
    except Exception as e:
        print(f"❌ General error: {e}")
        return 1
    
    print("✅ All tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 