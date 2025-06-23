import psycopg2
import hashlib
import os

# Database connection parameters
DB_PARAMS = {
    'dbname': 'pecantv',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',  # Use localhost since we're running outside Docker
    'port': '5433'        # Docker port mapping
}

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_test_user():
    """Reset or create test user with known credentials"""
    conn = psycopg2.connect(**DB_PARAMS)
    
    try:
        with conn.cursor() as cur:
            # Check if test user exists
            cur.execute("SELECT id FROM users WHERE email = %s", ('test@example.com',))
            user_exists = cur.fetchone()
            
            hashed_password = hash_password('password')
            
            if user_exists:
                # Update existing user
                cur.execute("""
                    UPDATE users 
                    SET password_hash = %s, first_name = %s, last_name = %s
                    WHERE email = %s
                """, (hashed_password, 'Test', 'User', 'test@example.com'))
                print("✅ Updated existing test user")
            else:
                # Create new user
                cur.execute("""
                    INSERT INTO users (email, password_hash, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                """, ('test@example.com', hashed_password, 'Test', 'User'))
                print("✅ Created new test user")
            
            conn.commit()
            print("🔐 Test user credentials:")
            print("   Email: test@example.com")
            print("   Password: password")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_test_user() 