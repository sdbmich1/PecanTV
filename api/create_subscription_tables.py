#!/usr/bin/env python3
"""
Script to create subscription tables in the database.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

def create_subscription_tables():
    """Create subscription-related tables in the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        print("🎬 Creating PecanTV Subscription Tables...")
        print("=" * 50)
        
        # Create subscription_plans table
        print("📋 Creating subscription_plans table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id SERIAL PRIMARY KEY,
                uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                interval VARCHAR(20) DEFAULT 'month',
                stripe_product_id VARCHAR(255) UNIQUE,
                stripe_price_id VARCHAR(255) UNIQUE,
                features JSONB,
                max_devices INTEGER DEFAULT 1,
                max_quality VARCHAR(10) DEFAULT '720p',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("✅ subscription_plans table created")
        
        # Create user_subscriptions table
        print("📋 Creating user_subscriptions table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                id SERIAL PRIMARY KEY,
                uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                plan_id INTEGER REFERENCES subscription_plans(id),
                stripe_subscription_id VARCHAR(255) UNIQUE,
                stripe_customer_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'active',
                current_period_start TIMESTAMP WITH TIME ZONE,
                current_period_end TIMESTAMP WITH TIME ZONE,
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                trial_end TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("✅ user_subscriptions table created")
        
        # Create subscription_history table
        print("📋 Creating subscription_history table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscription_history (
                id SERIAL PRIMARY KEY,
                uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                subscription_id INTEGER REFERENCES user_subscriptions(id) ON DELETE CASCADE,
                event_type VARCHAR(50) NOT NULL,
                event_data JSONB,
                stripe_event_id VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("✅ subscription_history table created")
        
        # Add indexes for better performance
        print("📋 Creating indexes...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_subscription_history_user_id ON subscription_history(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_subscription_history_event_type ON subscription_history(event_type)")
        print("✅ Indexes created")
        
        # Add stripe_customer_id column to users table if it doesn't exist
        print("📋 Checking users table for stripe_customer_id...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'stripe_customer_id'
        """)
        
        if not cur.fetchone():
            print("📋 Adding stripe_customer_id to users table...")
            cur.execute("ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id)")
            print("✅ stripe_customer_id column added to users table")
        else:
            print("✅ stripe_customer_id column already exists in users table")
        
        # Insert default subscription plans
        print("📋 Inserting default subscription plans...")
        default_plans = [
            {
                'name': 'Free',
                'description': 'Limited access to basic content',
                'price': 0.00,
                'features': {
                    'episodes_per_month': 3,
                    'quality': '480p',
                    'ads': True,
                    'devices': 1,
                    'downloads': False
                },
                'max_devices': 1,
                'max_quality': '480p'
            },
            {
                'name': 'Basic',
                'description': 'Unlimited episodes with no ads',
                'price': 9.99,
                'features': {
                    'episodes_per_month': -1,
                    'quality': '720p',
                    'ads': False,
                    'devices': 1,
                    'downloads': False
                },
                'max_devices': 1,
                'max_quality': '720p'
            },
            {
                'name': 'Premium',
                'description': 'High quality streaming with downloads',
                'price': 14.99,
                'features': {
                    'episodes_per_month': -1,
                    'quality': '1080p',
                    'ads': False,
                    'devices': 2,
                    'downloads': True
                },
                'max_devices': 2,
                'max_quality': '1080p'
            },
            {
                'name': 'Family',
                'description': 'Perfect for the whole family',
                'price': 19.99,
                'features': {
                    'episodes_per_month': -1,
                    'quality': '1080p',
                    'ads': False,
                    'devices': 4,
                    'downloads': True,
                    'parental_controls': True,
                    'family_profiles': True
                },
                'max_devices': 4,
                'max_quality': '1080p'
            }
        ]
        
        for plan in default_plans:
            cur.execute("""
                INSERT INTO subscription_plans (name, description, price, features, max_devices, max_quality)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            """, (
                plan['name'],
                plan['description'],
                plan['price'],
                plan['features'],
                plan['max_devices'],
                plan['max_quality']
            ))
        
        print("✅ Default subscription plans inserted")
        
        conn.commit()
        print("\n🎉 All subscription tables created successfully!")
        
        # Verify tables were created
        print("\n📊 Verifying tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('subscription_plans', 'user_subscriptions', 'subscription_history')
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        for table in tables:
            print(f"✅ {table[0]} table exists")
        
        # Show subscription plans
        print("\n📋 Available subscription plans:")
        cur.execute("SELECT id, name, price, max_devices, max_quality FROM subscription_plans ORDER BY price")
        plans = cur.fetchall()
        
        for plan in plans:
            print(f"  • {plan[1]} - ${plan[2]}/month - {plan[3]} device(s) - {plan[4]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_subscription_tables() 