import Foundation

class FavoritesManager: ObservableObject {
    static let shared = FavoritesManager()
    
    @Published private(set) var favoriteIds: Set<Int> = []
    private let defaults = UserDefaults.standard
    private let favoritesKey = "favoriteContentIds"
    
    // For now, we'll use a default user ID of 1
    // In a real app, this would come from authentication
    private let currentUserId = 1
    private let baseURL = "http://localhost:8000"
    
    private init() {
        loadFavorites()
    }
    
    func toggleFavorite(_ content: MediaContent) {
        if favoriteIds.contains(content.id) {
            favoriteIds.remove(content.id)
        } else {
            favoriteIds.insert(content.id)
        }
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
        do {
            let url = URL(string: "\(baseURL)/favorites/\(currentUserId)")!
            let (data, _) = try await URLSession.shared.data(from: url)
            
            let response = try JSONDecoder().decode(FavoritesResponse.self, from: data)
            
            DispatchQueue.main.async {
                self.favoriteIds = Set(response.favorites.map { $0.id })
                self.saveFavorites()
            }
        } catch {
            print("Failed to load favorites from database: \(error)")
            // Fall back to local storage
        }
    }
    
    private func syncFavoriteWithDatabase(contentId: Int, isFavorited: Bool) async {
        do {
            let url = URL(string: "\(baseURL)/favorites/\(currentUserId)/toggle/\(contentId)")!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let (data, _) = try await URLSession.shared.data(for: request)
            let response = try JSONDecoder().decode(FavoriteToggleResponse.self, from: data)
            
            print("Favorite sync response: \(response.message)")
        } catch {
            print("Failed to sync favorite with database: \(error)")
            // The local state is already updated, so we don't need to revert
        }
    }
    
    private func loadFavorites() {
        if let savedIds = defaults.array(forKey: favoritesKey) as? [Int] {
            favoriteIds = Set(savedIds)
        }
    }
    
    private func saveFavorites() {
        defaults.set(Array(favoriteIds), forKey: favoritesKey)
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