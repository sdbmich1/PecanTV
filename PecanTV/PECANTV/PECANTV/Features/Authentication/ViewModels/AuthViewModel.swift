import Foundation
// import FirebaseAuth
// import FirebaseCore
// import FirebaseFirestore

@MainActor
class AuthViewModel: ObservableObject {
    // @Published var firebaseUser: FirebaseAuth.User?
    @Published var currentUser: User?
    @Published var isAuthenticated = false
    @Published var error: Error?
    @Published var isLoading = false
    
    // Callback for when authentication succeeds
    var onAuthenticationSuccess: (() -> Void)?
    
    // API base URL - using centralized configuration
    
    // private var authStateHandler: AuthStateDidChangeListenerHandle?
    // private let db = Firestore.firestore()
    
    private let userDefaults = UserDefaults.standard
    private let usersKey = "stored_users"
    
    init() {
        // Check if user is already authenticated (stored in UserDefaults)
        if let userData = UserDefaults.standard.data(forKey: "current_user"),
           let user = try? JSONDecoder().decode(User.self, from: userData) {
            currentUser = user
            isAuthenticated = true
            print("🔄 Restored authenticated user: \(user.fullName)")
        }
        
        // Listen for token expiration notifications
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleTokenExpirationNotification),
            name: .tokenExpired,
            object: nil
        )
    }
    
    deinit {
        // if let handler = authStateHandler {
        //     Auth.auth().removeStateDidChangeListener(handler)
        // }
        NotificationCenter.default.removeObserver(self)
    }
    
    @objc private func handleTokenExpirationNotification() {
        print("🔄 Received token expiration notification")
        
        // First, try to refresh the token instead of immediately signing out
        Task {
            let refreshSuccess = await refreshToken()
            if !refreshSuccess {
                // Only sign out if token refresh fails
                print("🔄 Token refresh failed, signing out user")
                handleTokenExpiration()
            } else {
                print("🔄 Token refreshed successfully")
            }
        }
    }
    
    // MARK: - User Storage
    private func storeUser(_ user: User, password: String) {
        var users = getStoredUsers()
        users[user.email] = user
        
        print("💾 Storing user: \(user.email) - Total users: \(users.count)")
        
        if let data = try? JSONEncoder().encode(users) {
            userDefaults.set(data, forKey: usersKey)
            print("✅ User data encoded and stored successfully")
        } else {
            print("❌ Failed to encode user data")
        }
        
        // Store password separately
        userDefaults.set(password, forKey: "password_\(user.email)")
        print("🔐 Password stored for: \(user.email)")
    }
    
    private func getStoredUsers() -> [String: User] {
        guard let data = userDefaults.data(forKey: usersKey),
              let users = try? JSONDecoder().decode([String: User].self, from: data) else {
            print("📭 No stored users found or failed to decode")
            return [:]
        }
        print("📊 Retrieved \(users.count) stored users")
        return users
    }
    
    private func validateCredentials(email: String, password: String) -> User? {
        let users = getStoredUsers()
        guard let user = users[email] else {
            print("❌ User not found: \(email)")
            return nil
        }
        
        let storedPassword = userDefaults.string(forKey: "password_\(email)")
        guard storedPassword == password else {
            print("❌ Password mismatch for: \(email)")
            return nil
        }
        
        print("✅ Credentials validated for: \(email)")
        return user
    }
    
    // MARK: - API Authentication Methods
    func signIn(email: String, password: String) async {
        isLoading = true
        error = nil
        
        print("🔐 Attempting API signin for: \(email)")
        
        guard let url = APIConfig.url(for: APIConfig.Endpoints.login) else {
            error = NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])
            isLoading = false
            return
        }
        
        let loginData = ["email": email, "password": password]
        
        do {
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: loginData)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("📡 Login response status: \(httpResponse.statusCode)")
                
                // Accept both 200 and 201 as success
                if httpResponse.statusCode == 200 || httpResponse.statusCode == 201 {
                    do {
                        // Parse the API response
                        let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)
                        
                        // Convert API user to app user
                        let user = User(
                            id: String(authResponse.user.id),
                            firstName: authResponse.user.first_name ?? "",
                            lastName: authResponse.user.last_name ?? "",
                            email: authResponse.user.email
                        )
                        
                        currentUser = user
                        isAuthenticated = true
                        
                        // Store user data locally
                        if let userData = try? JSONEncoder().encode(user) {
                            UserDefaults.standard.set(userData, forKey: "current_user")
                        }
                        
                        // Store access token
                        UserDefaults.standard.set(authResponse.access_token, forKey: "access_token")
                        
                        print("✅ API signin successful: \(user.fullName)")
                    } catch {
                        print("❌ Failed to parse login response: \(error)")
                        self.error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "Invalid response format"])
                    }
                } else {
                    // Handle error response
                    if let errorResponse = try? JSONDecoder().decode(APIError.self, from: data) {
                        error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorResponse.detail])
                    } else {
                        // Try to extract error message from response
                        if let responseString = String(data: data, encoding: .utf8) {
                            error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: responseString])
                        } else {
                            error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "Login failed"])
                        }
                    }
                    print("❌ API signin failed with status: \(httpResponse.statusCode)")
                }
            }
        } catch {
            self.error = error
            print("❌ API signin error: \(error.localizedDescription)")
        }
        
        print("📊 Final auth state - isAuthenticated: \(isAuthenticated), currentUser: \(currentUser?.fullName ?? "nil")")
        isLoading = false
        
        // Trigger content loading when authentication succeeds
        if isAuthenticated {
            onAuthenticationSuccess?()
        }
    }
    
    func signUp(email: String, password: String, firstName: String, lastName: String) async {
        isLoading = true
        error = nil
        
        print("🔐 Starting API signup for: \(email)")
        
        guard let url = APIConfig.url(for: APIConfig.Endpoints.register) else {
            error = NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])
            isLoading = false
            return
        }
        
        let registerData = [
            "email": email,
            "password": password,
            "first_name": firstName,
            "last_name": lastName
        ]
        
        do {
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: registerData)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("📡 Registration response status: \(httpResponse.statusCode)")
                
                // Accept both 200 and 201 as success
                if httpResponse.statusCode == 200 || httpResponse.statusCode == 201 {
                    do {
                        // Parse the API response
                        let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)
                        
                        // Convert API user to app user
                        let user = User(
                            id: String(authResponse.user.id),
                            firstName: authResponse.user.first_name ?? "",
                            lastName: authResponse.user.last_name ?? "",
                            email: authResponse.user.email
                        )
                        
                        currentUser = user
                        isAuthenticated = true
                        
                        // Store user data locally
                        if let userData = try? JSONEncoder().encode(user) {
                            UserDefaults.standard.set(userData, forKey: "current_user")
                        }
                        
                        // Store access token
                        UserDefaults.standard.set(authResponse.access_token, forKey: "access_token")
                        
                        print("✅ API signup successful: \(user.fullName)")
                    } catch {
                        print("❌ Failed to parse registration response: \(error)")
                        self.error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "Invalid response format"])
                    }
                } else {
                    // Handle error response
                    if let errorResponse = try? JSONDecoder().decode(APIError.self, from: data) {
                        error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorResponse.detail])
                    } else {
                        // Try to extract error message from response
                        if let responseString = String(data: data, encoding: .utf8) {
                            error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: responseString])
                        } else {
                            error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "Registration failed"])
                        }
                    }
                    print("❌ API signup failed with status: \(httpResponse.statusCode)")
                }
            }
        } catch {
            self.error = error
            print("❌ API signup error: \(error.localizedDescription)")
        }
        
        print("📊 Final auth state - isAuthenticated: \(isAuthenticated), currentUser: \(currentUser?.fullName ?? "nil")")
        isLoading = false
        
        // Trigger content loading when authentication succeeds
        if isAuthenticated {
            onAuthenticationSuccess?()
        }
    }
    
    func signOut() {
        currentUser = nil
        isAuthenticated = false
        UserDefaults.standard.removeObject(forKey: "current_user")
        UserDefaults.standard.removeObject(forKey: "access_token")
        
        // Clear favorites when user signs out
        clearFavoritesOnSignOut()
        
        print("🚪 User signed out")
    }
    
    private func clearFavoritesOnSignOut() {
        // Clear favorites from UserDefaults
        UserDefaults.standard.removeObject(forKey: "favoriteContentIds")
        print("🧹 Cleared favorites on sign out")
    }
    
    // MARK: - Token Management
    func getValidAccessToken() -> String? {
        guard let token = UserDefaults.standard.string(forKey: "access_token") else {
            print("⚠️ No access token found")
            return nil
        }
        
        // For now, we'll just return the token and let the API handle expiration
        // In a production app, you'd want to decode the JWT and check expiration
        return token
    }
    
    func handleTokenExpiration() {
        print("🔄 Token expired, signing out user")
        signOut()
    }
    
    func refreshToken() async -> Bool {
        // For now, we'll just return false since we don't have a refresh token endpoint
        // In a production app, you'd make a call to refresh the token
        print("🔄 Token refresh not implemented, user needs to sign in again")
        return false
    }
    
    // MARK: - Token Validation
    func isTokenValid() -> Bool {
        guard let token = UserDefaults.standard.string(forKey: "access_token") else {
            return false
        }
        
        // For now, we'll assume the token is valid if it exists
        // In a production app, you'd decode the JWT and check expiration
        return !token.isEmpty
    }
    
    // For testing purposes - clear all stored users
    func clearStoredUsers() {
        userDefaults.removeObject(forKey: usersKey)
        
        // Clear all password entries
        let users = getStoredUsers()
        for user in users.keys {
            userDefaults.removeObject(forKey: "password_\(user)")
        }
        
        print("🧹 Cleared all stored users")
    }
    
    func resetPassword(email: String) async {
        isLoading = true
        error = nil
        
        // Temporary mock password reset for testing
        isLoading = false
    }
}

// MARK: - API Response Models
struct APIUser: Codable {
    let id: Int
    let email: String
    let first_name: String?
    let last_name: String?
    let created_at: String
    let updated_at: String
}

struct AuthResponse: Codable {
    let user: APIUser
    let access_token: String
    let token_type: String
    let subscription_required: Bool?
    let subscription_plans: [SubscriptionPlan]?
}

struct SubscriptionPlan: Codable {
    let id: Int
    let name: String
    let description: String?
    let price: Int
    let currency: String
    let interval: String
    let features: [String]?
    let stripe_price_id: String?
}

struct APIError: Codable {
    let detail: String
}

// MARK: - Notification Names
extension Notification.Name {
    static let tokenExpired = Notification.Name("tokenExpired")
    static let contentLoaded = Notification.Name("contentLoaded")
}

 