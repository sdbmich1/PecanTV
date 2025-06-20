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
    
    // private var authStateHandler: AuthStateDidChangeListenerHandle?
    // private let db = Firestore.firestore()
    
    private let userDefaults = UserDefaults.standard
    private let usersKey = "stored_users"
    
    init() {
        // setupAuthStateListener()
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
    
    // MARK: - Authentication Methods
    func signIn(email: String, password: String) async {
        isLoading = true
        error = nil
        
        print("🔐 Attempting signin for: \(email)")
        
        // Check if it's the test user
        if email == "test@example.com" && password == "password" {
            currentUser = User(
                id: "mock-user-id",
                firstName: "Test",
                lastName: "User",
                email: email
            )
            isAuthenticated = true
            print("✅ Test user signed in successfully")
        } else {
            // Check stored users
            let users = getStoredUsers()
            print("📊 Found \(users.count) stored users")
            
            if let user = validateCredentials(email: email, password: password) {
                currentUser = user
                isAuthenticated = true
                print("✅ User signed in successfully: \(user.fullName)")
            } else {
                error = NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid credentials"])
                print("❌ Invalid credentials for: \(email)")
            }
        }
        
        print("📊 Final auth state - isAuthenticated: \(isAuthenticated), currentUser: \(currentUser?.fullName ?? "nil")")
        isLoading = false
        
        // Trigger content loading when authentication succeeds
        onAuthenticationSuccess?()
    }
    
    func signUp(email: String, password: String, firstName: String, lastName: String) async {
        isLoading = true
        error = nil
        
        print("🔐 Starting signup for: \(email)")
        
        // Check if user already exists
        let users = getStoredUsers()
        if users[email] != nil {
            error = NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "User with this email already exists"])
            print("❌ User already exists: \(email)")
            isLoading = false
            return
        }
        
        // Create new user
        let newUser = User(
            id: UUID().uuidString,
            firstName: firstName,
            lastName: lastName,
            email: email
        )
        
        print("✅ Created new user: \(newUser.fullName)")
        
        // Store the user
        storeUser(newUser, password: password)
        
        // Set as current user and authenticate
        currentUser = newUser
        isAuthenticated = true
        
        print("🎉 User signed up and authenticated: \(email)")
        print("📊 Current auth state - isAuthenticated: \(isAuthenticated), currentUser: \(currentUser?.fullName ?? "nil")")
        
        isLoading = false
        
        // Trigger content loading when authentication succeeds
        onAuthenticationSuccess?()
    }
    
    func signOut() {
        currentUser = nil
        isAuthenticated = false
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

 