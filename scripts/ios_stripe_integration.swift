
// Add to your iOS project:

// 1. Install Stripe SDK via Swift Package Manager:
// https://github.com/stripe/stripe-ios

// 2. Initialize Stripe in your AppDelegate or main app file:
import Stripe

class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        StripeAPI.defaultPublishableKey = "pk_live_51RbvsqA2wVeJL6q1X5xoNjoGvmazXemuBt55HPGwf1YNcT7MGBohDXaGOJnw8hKjw8LfVnJsioNqunI9MhwCTx4l00qPwRHPvd"
        return true
    }
}

// 3. Subscription service class:
class SubscriptionService {
    static let shared = SubscriptionService()
    private let baseURL = "http://localhost:8000"
    
    func getSubscriptionPlans() async throws -> [SubscriptionPlan] {
        let url = URL(string: "\(baseURL)/subscriptions/plans")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([SubscriptionPlan].self, from: data)
    }
    
    func createSubscription(planId: Int, customerId: String) async throws -> Subscription {
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
    }
}

// 4. Subscription view:
struct SubscriptionView: View {
    @State private var plans: [SubscriptionPlan] = []
    @State private var isLoading = true
    
    var body: some View {
        NavigationView {
            if isLoading {
                ProgressView("Loading plans...")
            } else {
                List(plans, id: \.id) { plan in
                    VStack(alignment: .leading) {
                        Text(plan.name)
                            .font(.headline)
                        Text(plan.description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        Text("$\(plan.price)/month")
                            .font(.title2)
                            .fontWeight(.bold)
                    }
                    .padding()
                }
            }
        }
        .task {
            await loadPlans()
        }
    }
    
    func loadPlans() async {
        do {
            plans = try await SubscriptionService.shared.getSubscriptionPlans()
            isLoading = false
        } catch {
            print("Error loading plans: \(error)")
            isLoading = false
        }
    }
}

// 5. Data models:
struct SubscriptionPlan: Codable {
    let id: Int
    let name: String
    let description: String
    let price: Double
    let stripeProductId: String?
    let stripePriceId: String?
    let features: [String: Any]
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, price
        case stripeProductId = "stripe_product_id"
        case stripePriceId = "stripe_price_id"
        case features
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        description = try container.decode(String.self, forKey: .description)
        price = try container.decode(Double.self, forKey: .price)
        stripeProductId = try container.decodeIfPresent(String.self, forKey: .stripeProductId)
        stripePriceId = try container.decodeIfPresent(String.self, forKey: .stripePriceId)
        features = [:] // Parse features as needed
    }
}

struct Subscription: Codable {
    let id: Int
    let customerId: String
    let planId: Int
    let status: String
    let stripeSubscriptionId: String?
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case customerId = "customer_id"
        case planId = "plan_id"
        case status
        case stripeSubscriptionId = "stripe_subscription_id"
        case createdAt = "created_at"
    }
}
