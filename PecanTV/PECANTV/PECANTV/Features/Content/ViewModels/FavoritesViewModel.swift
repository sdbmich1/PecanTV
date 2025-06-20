import SwiftUI

@MainActor
class FavoritesViewModel: ObservableObject {
    @Published private(set) var favorites: Set<Int> = []
    private let favoritesKey = "userFavorites"
    
    init() {
        Task {
            await loadFavorites()
        }
    }
    
    func isFavorite(_ content: MediaContent) -> Bool {
        favorites.contains(content.id)
    }
    
    func toggleFavorite(_ content: MediaContent) async {
        do {
            if favorites.contains(content.id) {
                favorites.remove(content.id)
            } else {
                favorites.insert(content.id)
            }
            try await saveFavorites()
        } catch {
            print("Error saving favorites: \(error.localizedDescription)")
        }
    }
    
    private func saveFavorites() async throws {
        let favoritesArray = Array(favorites)
        if let encoded = try? JSONEncoder().encode(favoritesArray) {
            UserDefaults.standard.set(encoded, forKey: favoritesKey)
        }
    }
    
    func loadFavorites() async {
        if let data = UserDefaults.standard.data(forKey: favoritesKey),
           let favoritesArray = try? JSONDecoder().decode([Int].self, from: data) {
            favorites = Set(favoritesArray)
        }
    }
} 