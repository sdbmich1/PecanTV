#!/usr/bin/env python3
"""
Comprehensive Stripe Integration Setup Script for PecanTV
This script handles:
1. Creating Stripe products and prices
2. Linking Stripe IDs to database
3. Testing API endpoints
4. Generating iOS integration code
"""

import os
import sys
import json
import requests
import psycopg2
import stripe
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../api/.env')

# Database connection parameters
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_K1HJErMqmX8g',
    'host': 'ep-blue-cherry-a6427e0b-pooler.us-west-2.aws.neon.tech',
    'port': '5432',
    'sslmode': 'require'
}

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

# API base URL (update this to your actual API URL)
API_BASE_URL = "http://localhost:8000"  # Change to your ngrok URL if needed

# Subscription plans configuration
SUBSCRIPTION_PLANS = [
    {
        'name': 'Basic',
        'description': 'Basic streaming access',
        'price': 4.99,
        'currency': 'usd',
        'interval': 'month',
        'features': {
            'hd_quality': False,
            'offline_downloads': False,
            'multiple_devices': False,
            'ad_free': False
        }
    },
    {
        'name': 'Premium',
        'description': 'Premium streaming with HD quality',
        'price': 9.99,
        'currency': 'usd',
        'interval': 'month',
        'features': {
            'hd_quality': True,
            'offline_downloads': True,
            'multiple_devices': True,
            'ad_free': True
        }
    },
    {
        'name': 'Family',
        'description': 'Family plan for up to 6 users',
        'price': 14.99,
        'currency': 'usd',
        'interval': 'month',
        'features': {
            'hd_quality': True,
            'offline_downloads': True,
            'multiple_devices': True,
            'ad_free': True,
            'family_sharing': True,
            'max_profiles': 6
        }
    }
]

def test_stripe_connection():
    """Test Stripe API connection."""
    print("🔌 Testing Stripe connection...")
    try:
        account = stripe.Account.retrieve()
        print(f"✅ Connected to Stripe account: {account.business_profile.name}")
        print(f"   Account ID: {account.id}")
        print(f"   Charges enabled: {account.charges_enabled}")
        print(f"   Payouts enabled: {account.payouts_enabled}")
        return True
    except Exception as e:
        print(f"❌ Stripe connection failed: {e}")
        return False

def create_stripe_products():
    """Create products and prices in Stripe."""
    print("\n🛍️  Creating Stripe products and prices...")
    
    products_created = []
    
    for plan in SUBSCRIPTION_PLANS:
        try:
            # Create product
            product = stripe.Product.create(
                name=f"PecanTV {plan['name']}",
                description=plan['description'],
                metadata={
                    'plan_type': plan['name'].lower(),
                    'features': json.dumps(plan['features'])
                }
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(plan['price'] * 100),  # Convert to cents
                currency=plan['currency'],
                recurring={'interval': plan['interval']},
                metadata={
                    'plan_type': plan['name'].lower(),
                    'features': json.dumps(plan['features'])
                }
            )
            
            products_created.append({
                'plan_name': plan['name'],
                'product_id': product.id,
                'price_id': price.id,
                'features': plan['features']
            })
            
            print(f"  ✅ Created {plan['name']} plan:")
            print(f"     Product ID: {product.id}")
            print(f"     Price ID: {price.id}")
            print(f"     Price: ${plan['price']}/{plan['interval']}")
            
        except Exception as e:
            print(f"  ❌ Failed to create {plan['name']} plan: {e}")
    
    return products_created

def update_database_with_stripe_ids(products_created):
    """Update database subscription plans with Stripe IDs."""
    print("\n💾 Updating database with Stripe IDs...")
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    try:
        for product in products_created:
            cur.execute("""
                UPDATE subscription_plans 
                SET stripe_product_id = %s, stripe_price_id = %s, updated_at = %s
                WHERE name = %s
            """, (
                product['product_id'],
                product['price_id'],
                datetime.now(timezone.utc),
                product['plan_name']
            ))
            
            if cur.rowcount > 0:
                print(f"  ✅ Updated {product['plan_name']} with Stripe IDs")
            else:
                print(f"  ⚠️  No rows updated for {product['plan_name']}")
        
        conn.commit()
        print("✅ Database updated successfully")
        
    except Exception as e:
        print(f"❌ Database update failed: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def test_api_endpoints():
    """Test the subscription API endpoints."""
    print("\n🧪 Testing API endpoints...")
    
    endpoints = [
        ('GET', '/subscriptions/plans', 'Get subscription plans'),
        ('GET', '/subscriptions/plans/1', 'Get specific plan'),
        ('POST', '/subscriptions/create', 'Create subscription (requires data)'),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            url = f"{API_BASE_URL}{endpoint}"
            print(f"\n  Testing {method} {endpoint} - {description}")
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                # For POST, we'll just test if the endpoint exists
                response = requests.post(url, json={}, timeout=10)
            
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"    Response: {response.text[:200]}...")
            elif response.status_code == 422:
                print("    ✅ Endpoint exists (validation error expected)")
            else:
                print(f"    Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"    ❌ Connection failed - make sure API is running")
        except Exception as e:
            print(f"    ❌ Error: {e}")

def generate_ios_integration_code():
    """Generate iOS integration code snippets."""
    print("\n📱 Generating iOS integration code...")
    
    ios_code = f'''
// Add to your iOS project:

// 1. Install Stripe SDK via Swift Package Manager:
// https://github.com/stripe/stripe-ios

// 2. Initialize Stripe in your AppDelegate or main app file:
import Stripe

class AppDelegate: UIResponder, UIApplicationDelegate {{
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {{
        StripeAPI.defaultPublishableKey = "{STRIPE_PUBLISHABLE_KEY}"
        return true
    }}
}}

// 3. Subscription service class:
class SubscriptionService {{
    static let shared = SubscriptionService()
    private let baseURL = "{API_BASE_URL}"
    
    func getSubscriptionPlans() async throws -> [SubscriptionPlan] {{
        let url = URL(string: "\(baseURL)/subscriptions/plans")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([SubscriptionPlan].self, from: data)
    }}
    
    func createSubscription(planId: Int, customerId: String) async throws -> Subscription {{
        let url = URL(string: "\(baseURL)/subscriptions/create")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "plan_id": planId,
            "customer_id": customerId
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(Subscription.self, from: data)
    }}
}}

// 4. Subscription view:
struct SubscriptionView: View {{
    @State private var plans: [SubscriptionPlan] = []
    @State private var isLoading = true
    
    var body: some View {{
        NavigationView {{
            if isLoading {{
                ProgressView("Loading plans...")
            }} else {{
                List(plans, id: \\.id) {{ plan in
                    VStack(alignment: .leading) {{
                        Text(plan.name)
                            .font(.headline)
                        Text(plan.description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        Text("$\(plan.price)/month")
                            .font(.title2)
                            .fontWeight(.bold)
                    }}
                    .padding()
                }}
            }}
        }}
        .task {{
            await loadPlans()
        }}
    }}
    
    func loadPlans() async {{
        do {{
            plans = try await SubscriptionService.shared.getSubscriptionPlans()
            isLoading = false
        }} catch {{
            print("Error loading plans: \\(error)")
            isLoading = false
        }}
    }}
}}

// 5. Data models:
struct SubscriptionPlan: Codable {{
    let id: Int
    let name: String
    let description: String
    let price: Double
    let stripeProductId: String?
    let stripePriceId: String?
    let features: [String: Any]
    
    enum CodingKeys: String, CodingKey {{
        case id, name, description, price
        case stripeProductId = "stripe_product_id"
        case stripePriceId = "stripe_price_id"
        case features
    }}
    
    init(from decoder: Decoder) throws {{
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        description = try container.decode(String.self, forKey: .description)
        price = try container.decode(Double.self, forKey: .price)
        stripeProductId = try container.decodeIfPresent(String.self, forKey: .stripeProductId)
        stripePriceId = try container.decodeIfPresent(String.self, forKey: .stripePriceId)
        features = [:] // Parse features as needed
    }}
}}

struct Subscription: Codable {{
    let id: Int
    let customerId: String
    let planId: Int
    let status: String
    let stripeSubscriptionId: String?
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {{
        case id
        case customerId = "customer_id"
        case planId = "plan_id"
        case status
        case stripeSubscriptionId = "stripe_subscription_id"
        case createdAt = "created_at"
    }}
}}
'''
    
    # Save to file
    with open('ios_stripe_integration.swift', 'w') as f:
        f.write(ios_code)
    
    print("✅ iOS integration code saved to 'ios_stripe_integration.swift'")

def create_webhook_endpoint():
    """Create Stripe webhook endpoint."""
    print("\n🔗 Creating Stripe webhook endpoint...")
    
    webhook_url = f"{API_BASE_URL}/subscriptions/webhook"
    
    try:
        webhook = stripe.WebhookEndpoint.create(
            url=webhook_url,
            enabled_events=[
                'customer.subscription.created',
                'customer.subscription.updated',
                'customer.subscription.deleted',
                'invoice.payment_succeeded',
                'invoice.payment_failed'
            ]
        )
        
        print(f"✅ Webhook created successfully:")
        print(f"   Webhook ID: {webhook.id}")
        print(f"   URL: {webhook.url}")
        print(f"   Secret: {webhook.secret}")
        print(f"\n⚠️  IMPORTANT: Add this webhook secret to your .env file:")
        print(f"   STRIPE_WEBHOOK_SECRET={webhook.secret}")
        
    except Exception as e:
        print(f"❌ Failed to create webhook: {e}")

def generate_test_script():
    """Generate a test script for manual testing."""
    print("\n🧪 Generating test script...")
    
    test_script = f'''#!/usr/bin/env python3
"""
Test script for PecanTV Stripe integration
Run this after setting up the integration to test all endpoints
"""

import requests
import json

API_BASE_URL = "{API_BASE_URL}"

def test_subscription_plans():
    """Test getting subscription plans."""
    print("Testing subscription plans endpoint...")
    response = requests.get(f"{{API_BASE_URL}}/subscriptions/plans")
    print(f"Status: {{response.status_code}}")
    if response.status_code == 200:
        plans = response.json()
        print(f"Found {{len(plans)}} plans:")
        for plan in plans:
            print(f"  - {{plan['name']}}: ${{plan['price']}}/month")
    else:
        print(f"Error: {{response.text}}")

def test_create_subscription():
    """Test creating a subscription."""
    print("\\nTesting subscription creation...")
    data = {{
        "plan_id": 1,
        "customer_id": "test_customer_123"
    }}
    response = requests.post(f"{{API_BASE_URL}}/subscriptions/create", json=data)
    print(f"Status: {{response.status_code}}")
    if response.status_code == 200:
        subscription = response.json()
        print(f"Created subscription: {{subscription}}")
    else:
        print(f"Error: {{response.text}}")

if __name__ == "__main__":
    test_subscription_plans()
    test_create_subscription()
'''
    
    with open('test_stripe_api.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Test script saved to 'test_stripe_api.py'")

def main():
    """Main execution function."""
    print("🚀 PecanTV Stripe Integration Setup")
    print("=" * 50)
    
    # Check if Stripe keys are configured
    if not stripe.api_key or not STRIPE_PUBLISHABLE_KEY:
        print("❌ Stripe keys not found in .env file")
        print("Please ensure STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY are set")
        return
    
    # Test Stripe connection
    if not test_stripe_connection():
        return
    
    # Create products and prices
    products_created = create_stripe_products()
    if not products_created:
        print("❌ No products were created")
        return
    
    # Update database
    update_database_with_stripe_ids(products_created)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Generate iOS code
    generate_ios_integration_code()
    
    # Create webhook
    create_webhook_endpoint()
    
    # Generate test script
    generate_test_script()
    
    print("\n🎉 Stripe integration setup complete!")
    print("\nNext steps:")
    print("1. Add the webhook secret to your .env file")
    print("2. Test the API endpoints with the generated test script")
    print("3. Integrate the iOS code into your app")
    print("4. Test the full subscription flow")

if __name__ == "__main__":
    main() 