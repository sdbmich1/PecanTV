// import FirebaseCore
// import FirebaseAuth

class FirebaseManager {
    static let shared = FirebaseManager()
    
    private init() {}
    
    func configure() {
        // Temporarily disabled until we get GoogleService-Info.plist
        // guard let filePath = Bundle.main.path(forResource: "GoogleService-Info", ofType: "plist") else {
        //     print("GoogleService-Info.plist not found")
        //     return
        // }
        // 
        // guard let options = FirebaseOptions(contentsOfFile: filePath) else {
        //     print("Failed to load Firebase options")
        //     return
        // }
        // 
        // FirebaseApp.configure(options: options)
    }
    
    // func signUp(email: String, password: String) async throws -> AuthDataResult {
    //     return try await Auth.auth().createUser(withEmail: email, password: password)
    // }
    // 
    // func signIn(email: String, password: String) async throws -> AuthDataResult {
    //     return try await Auth.auth().signIn(withEmail: email, password: password)
    // }
    // 
    // func signOut() throws {
    //     try Auth.auth().signOut()
    // }
} 