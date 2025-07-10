import Foundation

struct APIConfig {
    // Centralized API base URL configuration
    // Change this to switch between local development and production
    static let baseURL = "http://localhost:8000" // Use 8000 for local FastAPI
    
    // Alternative URLs for different environments
    static let ngrokURL = "https://YOUR_NGROK_URL" // Set this to your ngrok tunnel for remote access
    static let productionURL = "https://api.pecantv.com"
    
    // Endpoints
    enum Endpoints {
        static let health = "\(baseURL)/health"
        static let content = "\(baseURL)/content"
        static let auth = "\(baseURL)/auth"
        static let favorites = "\(baseURL)/favorites"
        static let subscriptions = "\(baseURL)/subscriptions"
        static let series = "\(baseURL)/series"
        static let episodes = "\(baseURL)/episodes"
        static let genres = "\(baseURL)/genres"
        static let ratings = "\(baseURL)/ratings"
        static let search = "\(baseURL)/search"
        
        // Auth specific endpoints
        static let login = "\(auth)/login"
        static let register = "\(auth)/register"
        static let me = "\(auth)/me"
        
        // Content specific endpoints
        static func contentById(_ id: Int) -> String {
            return "\(content)/\(id)"
        }
        
        static func contentEpisodes(_ contentId: Int) -> String {
            return "\(content)/\(contentId)/episodes"
        }
        
        static func seriesEpisodes(_ seriesId: Int) -> String {
            return "\(series)/\(seriesId)/episodes"
        }
        
        static func favoritesForUser(_ userId: Int) -> String {
            return "\(favorites)/\(userId)"
        }
        
        static func toggleFavorite(_ userId: Int, contentId: Int) -> String {
            return "\(favorites)/\(userId)/toggle/\(contentId)"
        }
        
        static func searchContent(_ query: String) -> String {
            let encodedQuery = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
            return "\(search)?q=\(encodedQuery)"
        }
    }
    
    // Helper method to get URL for any endpoint
    static func url(for endpoint: String) -> URL? {
        return URL(string: endpoint)
    }
    
    // Helper method to get base URL as URL
    static var baseURLAsURL: URL? {
        return URL(string: baseURL)
    }
} 