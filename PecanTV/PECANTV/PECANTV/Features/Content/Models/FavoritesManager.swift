import Foundation

@MainActor
class FavoritesManager: ObservableObject {
    static let shared = FavoritesManager()
    
    @Published private(set) var favoriteIds: Set<Int> = []
    @Published private(set) var favoriteContent: [MediaContent] = []
    private let defaults = UserDefaults.standard
    private let favoritesKey = "favoriteContentIds"
    
    // Get current user ID from AuthViewModel
    private var currentUserId: Int? {
        // Try to get from UserDefaults first
        if let userData = UserDefaults.standard.data(forKey: "current_user"),
           let user = try? JSONDecoder().decode(User.self, from: userData) {
            return Int(user.id)
        }
        return nil
    }
    
    init() {
        loadFavorites()
        // Load favorites from database on startup
        Task {
            await loadFavoritesFromDatabase()
        }
    }
    
    func toggleFavorite(_ content: MediaContent) {
        print("🔄 Toggling favorite for content: \(content.title) (ID: \(content.id))")
        print("🔍 Current favorite IDs: \(favoriteIds)")
        
        if favoriteIds.contains(content.id) {
            favoriteIds.remove(content.id)
            favoriteContent.removeAll { $0.id == content.id }
            print("❌ Removed from favorites: \(content.title)")
        } else {
            favoriteIds.insert(content.id)
            favoriteContent.append(content)
            print("✅ Added to favorites: \(content.title)")
        }
        
        print("🔍 Updated favorite IDs: \(favoriteIds)")
        print("🔍 Updated favorite content count: \(favoriteContent.count)")
        
        saveFavorites()
        
        // Sync with database
        Task {
            await syncFavoriteWithDatabase(contentId: content.id, isFavorited: favoriteIds.contains(content.id))
        }
    }
    
    func isFavorite(_ content: MediaContent) -> Bool {
        favoriteIds.contains(content.id)
    }
    
    func loadFavoritesFromDatabase() async {
        guard let userId = currentUserId else {
            print("⚠️ No authenticated user found for favorites")
            return
        }
        
        print("🔍 Current user ID: \(userId)")
        
        // Get the access token from UserDefaults
        guard let accessToken = UserDefaults.standard.string(forKey: "access_token") else {
            print("⚠️ No access token found for favorites")
            print("🔍 Available UserDefaults keys: \(UserDefaults.standard.dictionaryRepresentation().keys.filter { $0.contains("token") || $0.contains("auth") || $0.contains("user") })")
            return
        }
        
        print("🔍 Access token found: \(String(accessToken.prefix(20)))...")
        
        do {
            let url = URL(string: APIConfig.Endpoints.favoritesForUser(userId))!
            var request = URLRequest(url: url)
            request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("📡 Favorites response status: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode == 200 {
                    let response = try JSONDecoder().decode(FavoritesResponse.self, from: data)
                    
                    DispatchQueue.main.async {
                        self.favoriteIds = Set(response.favorites.map { $0.id })
                        self.favoriteContent = response.favorites
                        self.saveFavorites()
                        print("✅ Loaded \(response.favorites.count) favorites from database for user \(userId)")
                        print("📋 Favorite content: \(response.favorites.map { $0.title })")
                    }
                } else if httpResponse.statusCode == 401 {
                    print("❌ Token expired (401), handling token expiration")
                    if let errorText = String(data: data, encoding: .utf8) {
                        print("❌ Error response: \(errorText)")
                    }
                    // Handle token expiration but don't clear local favorites
                    await handleTokenExpiration()
                } else {
                    print("❌ Favorites API returned status: \(httpResponse.statusCode)")
                    if let errorText = String(data: data, encoding: .utf8) {
                        print("❌ Error response: \(errorText)")
                    }
                    // Don't clear local favorites on API errors
                }
            }
        } catch {
            print("❌ Failed to load favorites from database: \(error)")
            // Keep local favorites even if database loading fails
            print("🔍 Keeping existing local favorites: \(favoriteIds)")
        }
    }
    
    private func syncFavoriteWithDatabase(contentId: Int, isFavorited: Bool) async {
        guard let userId = currentUserId else {
            print("⚠️ No authenticated user found for favorite sync")
            return
        }
        
        print("🔍 Syncing favorite for user \(userId), content \(contentId), isFavorited: \(isFavorited)")
        
        // Get the access token from UserDefaults
        guard let accessToken = UserDefaults.standard.string(forKey: "access_token") else {
            print("⚠️ No access token found for favorite sync")
            print("🔍 Available UserDefaults keys: \(UserDefaults.standard.dictionaryRepresentation().keys.filter { $0.contains("token") || $0.contains("auth") || $0.contains("user") })")
            return
        }
        
        print("🔍 Access token found for sync: \(String(accessToken.prefix(20)))...")
        
        do {
            let url = URL(string: APIConfig.Endpoints.toggleFavorite(userId, contentId: contentId))!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("📡 Favorite toggle response status: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode == 200 {
                    let response = try JSONDecoder().decode(FavoriteToggleResponse.self, from: data)
                    print("Favorite sync response for user \(userId): \(response.message)")
                } else if httpResponse.statusCode == 401 {
                    print("❌ Token expired (401) during favorite sync, handling token expiration")
                    if let errorText = String(data: data, encoding: .utf8) {
                        print("❌ Error response: \(errorText)")
                    }
                    // Handle token expiration
                    await handleTokenExpiration()
                } else {
                    print("❌ Favorite toggle API returned status: \(httpResponse.statusCode)")
                    if let errorText = String(data: data, encoding: .utf8) {
                        print("❌ Error response: \(errorText)")
                    }
                }
            }
        } catch {
            print("Failed to sync favorite with database: \(error)")
            // The local state is already updated, so we don't need to revert
        }
    }
    
    private func handleTokenExpiration() async {
        print("🔄 Handling token expiration in FavoritesManager")
        
        // First, try to refresh the token instead of immediately clearing favorites
        // For now, we'll just post the notification and let the AuthViewModel handle it
        // This prevents aggressive clearing of favorites
        
        // Post notification to handle token expiration
        DispatchQueue.main.async {
            NotificationCenter.default.post(name: .tokenExpired, object: nil)
        }
        
        // Only clear favorites if we're sure the user is signed out
        // This will be handled by the AuthViewModel when it actually signs out the user
    }
    
    private func getAuthViewModel() -> AuthViewModel? {
        // This is a simple way to get the AuthViewModel
        // In a real app, you might want to use dependency injection
        return nil // We'll handle this differently
    }
    
    func loadFavorites() {
        print("🔍 Loading favorites...")
        if let savedIds = defaults.array(forKey: favoritesKey) as? [Int] {
            favoriteIds = Set(savedIds)
            print("🔍 Loaded \(savedIds.count) favorite IDs from local storage: \(savedIds)")
            
            // If we have favorite IDs but no content, try to populate from available content
            if !favoriteIds.isEmpty && favoriteContent.isEmpty {
                print("🔍 Attempting to populate favorite content from available content")
                populateFavoriteContentFromAvailableContent()
            }
        } else {
            print("🔍 No saved favorite IDs found in local storage")
        }
        
        // Also reload from database, but don't clear local favorites if it fails
        Task {
            await loadFavoritesFromDatabase()
        }
    }
    
    private func populateFavoriteContentFromAvailableContent() {
        // This method will be called by ContentViewModel when content is loaded
        print("🔍 populateFavoriteContentFromAvailableContent called")
    }
    
    func updateFavoriteContentFromAvailableContent(_ availableContent: [MediaContent]) {
        print("🔍 Updating favorite content from \(availableContent.count) available items")
        
        let favoriteContentItems = availableContent.filter { favoriteIds.contains($0.id) }
        print("🔍 Found \(favoriteContentItems.count) favorite items in available content")
        
        DispatchQueue.main.async {
            self.favoriteContent = favoriteContentItems
            print("🔍 Updated favorite content to \(self.favoriteContent.count) items")
            print("🔍 Favorite titles: \(self.favoriteContent.map { $0.title })")
        }
    }
    
    private func saveFavorites() {
        let favoriteIdsArray = Array(favoriteIds)
        defaults.set(favoriteIdsArray, forKey: favoritesKey)
        print("💾 Saved \(favoriteIdsArray.count) favorite IDs to local storage: \(favoriteIdsArray)")
    }
}

// API Response structures
struct FavoritesResponse: Codable {
    let favorites: [MediaContent]
    let totalCount: Int
    
    enum CodingKeys: String, CodingKey {
        case favorites
        case totalCount = "total_count"
    }
}

struct FavoriteToggleResponse: Codable {
    let success: Bool
    let message: String
    let isFavorited: Bool
    
    enum CodingKeys: String, CodingKey {
        case success
        case message
        case isFavorited = "is_favorited"
    }
} 