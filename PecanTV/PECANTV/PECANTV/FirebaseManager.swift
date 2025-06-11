import Foundation
import FirebaseCore
import FirebaseAuth

class FirebaseManager {
    static let shared = FirebaseManager()
    
    private init() {
        setupFirebase()
    }
    
    private func setupFirebase() {
        // Get the path to GoogleService-Info.plist
        guard let filePath = Bundle.main.path(forResource: "GoogleService-Info", ofType: "plist") else {
            fatalError("Couldn't find GoogleService-Info.plist")
        }
        
        // Create Firebase options
        guard let options = FirebaseOptions(contentsOfFile: filePath) else {
            fatalError("Couldn't load GoogleService-Info.plist")
        }
        
        // Configure Firebase
        FirebaseApp.configure(options: options)
    }
    
    func signUp(email: String, password: String) async throws -> AuthDataResult {
        return try await Auth.auth().createUser(withEmail: email, password: password)
    }
    
    func signIn(email: String, password: String) async throws -> AuthDataResult {
        return try await Auth.auth().signIn(withEmail: email, password: password)
    }
    
    func signOut() throws {
        try Auth.auth().signOut()
    }
} 