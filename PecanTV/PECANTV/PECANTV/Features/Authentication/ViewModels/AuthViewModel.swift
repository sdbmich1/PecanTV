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
    
    // API base URL - using your Mac's IP address
    private let baseURL = "http://localhost:8000"
    
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
    }
    
    deinit {
        // if let handler = authStateHandler {
        //     Auth.auth().removeStateDidChangeListener(handler)
        // }
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
        
        guard let url = URL(string: "\(baseURL)/auth/login") else {
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
                if httpResponse.statusCode == 200 {
                    // Parse the API response
                    let apiUser = try JSONDecoder().decode(APIUser.self, from: data)
                    
                    // Convert API user to app user
                    let user = User(
                        id: String(apiUser.id),
                        firstName: apiUser.first_name ?? "",
                        lastName: apiUser.last_name ?? "",
                        email: apiUser.email
                    )
                    
                    currentUser = user
                    isAuthenticated = true
                    
                    // Store user data locally
                    if let userData = try? JSONEncoder().encode(user) {
                        UserDefaults.standard.set(userData, forKey: "current_user")
                    }
                    
                    print("✅ API signin successful: \(user.fullName)")
                } else {
                    // Handle error response
                    if let errorResponse = try? JSONDecoder().decode(APIError.self, from: data) {
                        error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorResponse.detail])
                    } else {
                        error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "Login failed"])
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
        
        guard let url = URL(string: "\(baseURL)/auth/register") else {
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
                if httpResponse.statusCode == 200 {
                    // Parse the API response
                    let apiUser = try JSONDecoder().decode(APIUser.self, from: data)
                    
                    // Convert API user to app user
                    let user = User(
                        id: String(apiUser.id),
                        firstName: apiUser.first_name ?? "",
                        lastName: apiUser.last_name ?? "",
                        email: apiUser.email
                    )
                    
                    currentUser = user
                    isAuthenticated = true
                    
                    // Store user data locally
                    if let userData = try? JSONEncoder().encode(user) {
                        UserDefaults.standard.set(userData, forKey: "current_user")
                    }
                    
                    print("✅ API signup successful: \(user.fullName)")
                } else {
                    // Handle error response
                    if let errorResponse = try? JSONDecoder().decode(APIError.self, from: data) {
                        error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: errorResponse.detail])
                    } else {
                        error = NSError(domain: "", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "Registration failed"])
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
        print("🚪 User signed out")
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

struct APIError: Codable {
    let detail: String
}

 