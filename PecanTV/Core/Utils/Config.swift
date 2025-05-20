import Foundation

enum Config {
    static let apiBaseURL = "https://api.pecantv.com" // Replace with your actual API endpoint
    
    enum Endpoints {
        static let auth = "\(Config.apiBaseURL)/auth"
        static let content = "\(Config.apiBaseURL)/content"
        
        static func signIn() -> String { "\(auth)/signin" }
        static func signUp() -> String { "\(auth)/signup" }
        static func trending() -> String { "\(content)/trending" }
        static func continueWatching() -> String { "\(content)/continue-watching" }
        static func recommended() -> String { "\(content)/recommended" }
        static func content(id: String) -> String { "\(content)/\(id)" }
        static func search(query: String) -> String {
            let encodedQuery = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
            return "\(content)/search?q=\(encodedQuery)"
        }
        static func genre(_ genre: String) -> String {
            let encodedGenre = genre.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
            return "\(content)/genre/\(encodedGenre)"
        }
    }
    
    enum UserDefaultsKeys {
        static let authToken = "authToken"
        static let currentUser = "currentUser"
    }
} 