import Foundation

class FavoritesManager: ObservableObject {
    @Published private(set) var favoriteIds: Set<Int> = []
    private let defaults = UserDefaults.standard
    private let favoritesKey = "favoriteContentIds"
    
    init() {
        loadFavorites()
    }
    
    func toggleFavorite(_ content: MediaContent) {
        if favoriteIds.contains(content.id) {
            favoriteIds.remove(content.id)
        } else {
            favoriteIds.insert(content.id)
        }
        saveFavorites()
    }
    
    func isFavorite(_ content: MediaContent) -> Bool {
        favoriteIds.contains(content.id)
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