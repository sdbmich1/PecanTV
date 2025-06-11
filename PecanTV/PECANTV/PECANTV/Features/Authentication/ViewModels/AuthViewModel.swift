import Foundation
import FirebaseAuth
import FirebaseCore
import FirebaseFirestore

@MainActor
class AuthViewModel: ObservableObject {
    @Published var firebaseUser: FirebaseAuth.User?
    @Published var currentUser: User?
    @Published var isAuthenticated = false
    @Published var error: Error?
    @Published var isLoading = false
    
    private var authStateHandler: AuthStateDidChangeListenerHandle?
    private let db = Firestore.firestore()
    
    init() {
        setupAuthStateListener()
    }
    
    deinit {
        if let handler = authStateHandler {
            Auth.auth().removeStateDidChangeListener(handler)
        }
    }
    
    private func setupAuthStateListener() {
        authStateHandler = Auth.auth().addStateDidChangeListener { [weak self] _, user in
            self?.firebaseUser = user
            self?.isAuthenticated = user != nil
            if let user = user {
                Task {
                    await self?.fetchUserData(userId: user.uid)
                }
            } else {
                self?.currentUser = nil
            }
        }
    }
    
    private func fetchUserData(userId: String) async {
        do {
            let document = try await db.collection("users").document(userId).getDocument()
            if document.exists,
               let data = document.data() {
                currentUser = User(
                    id: userId,
                    firstName: data["firstName"] as? String ?? "",
                    lastName: data["lastName"] as? String ?? "",
                    email: data["email"] as? String ?? ""
                )
            }
        } catch {
            self.error = error
        }
    }
    
    func signIn(email: String, password: String) async {
        isLoading = true
        error = nil
        
        do {
            let result = try await Auth.auth().signIn(withEmail: email, password: password)
            firebaseUser = result.user
            isAuthenticated = true
            await fetchUserData(userId: result.user.uid)
        } catch {
            self.error = error
        }
        
        isLoading = false
    }
    
    func signUp(email: String, password: String, firstName: String, lastName: String) async {
        isLoading = true
        error = nil
        
        do {
            let result = try await Auth.auth().createUser(withEmail: email, password: password)
            
            let userData: [String: Any] = [
                "firstName": firstName,
                "lastName": lastName,
                "email": email,
                "createdAt": FieldValue.serverTimestamp()
            ]
            
            try await db.collection("users").document(result.user.uid).setData(userData)
            
            firebaseUser = result.user
            currentUser = User(
                id: result.user.uid,
                firstName: firstName,
                lastName: lastName,
                email: email
            )
            isAuthenticated = true
        } catch {
            self.error = error
        }
        
        isLoading = false
    }
    
    func signOut() {
        do {
            try Auth.auth().signOut()
            firebaseUser = nil
            currentUser = nil
            isAuthenticated = false
        } catch {
            self.error = error
        }
    }
    
    func resetPassword(email: String) async {
        isLoading = true
        error = nil
        
        do {
            try await Auth.auth().sendPasswordReset(withEmail: email)
        } catch {
            self.error = error
        }
        
        isLoading = false
    }
}

struct User: Identifiable, Codable {
    let id: String
    let firstName: String
    let lastName: String
    let email: String
    
    var fullName: String {
        "\(firstName) \(lastName)"
    }
} 