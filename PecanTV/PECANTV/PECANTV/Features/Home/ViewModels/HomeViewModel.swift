import SwiftUI
import Foundation
import Combine

actor ContentLoader {
    private var loadedContent: [MediaContent] = []
    private let driveService: GoogleDriveService
    
    init(driveService: GoogleDriveService) {
        self.driveService = driveService
    }
    
    func loadContent() async throws -> [MediaContent] {
        loadedContent = []
        
        // Actual content data
        let contentData = [
            MediaContent(
                id: 1,
                title: "Get Christie Love",
                posterURL: "https://storage.googleapis.com/pecantv_title_images/GetChristieLove-Feature-Img-16x9.png",
                trailerURL: "https://storage.googleapis.com/pecantv_trailers/GetChristieLove_Trailer_35sFinal.mp4",
                contentURL: "https://storage.googleapis.com/pecantv_content/getchristielove.mp4",
                description: "A groundbreaking crime drama series following the adventures of Christie Love, a stylish and tough undercover police detective.",
                type: "SERIES",
                runtime: 60,
                genre: "Crime",
                ageRating: "TV-14"
            ),
            MediaContent(
                id: 8,
                title: "Black Brigade",
                posterURL: "https://storage.googleapis.com/pecantv_title_images/Black-Brigade-Feature-Img.png",
                trailerURL: "https://storage.googleapis.com/pecantv_trailers/BlackBrigade_Trailer_35sFinal.mp4",
                contentURL: "https://storage.googleapis.com/pecantv_content/blackbrigade.mp4",
                description: "A racist officer is put in charge of a squad of black troops charged with taking an important bridge from the Germans.",
                type: "FILM",
                runtime: 70,
                genre: "Drama",
                ageRating: "PG-13"
            )
        ]
        
        for content in contentData {
            do {
                let formattedTitle = GoogleDriveConfig.formatTitle(content.title)
                
                // Get poster URL
                let posterURL = try await driveService.getTitleImageURL(for: formattedTitle)
                
                // Get trailer URL
                let trailerURL = try await driveService.getTrailerURL(for: formattedTitle)
                
                // Create a new MediaContent instance with the updated URLs
                let updatedContent = MediaContent(
                    id: content.id,
                    title: content.title,
                    posterURL: posterURL.absoluteString,
                    trailerURL: trailerURL.absoluteString,
                    contentURL: content.contentURL,
                    description: content.description,
                    type: content.type,
                    runtime: content.runtime,
                    genre: content.genre,
                    ageRating: content.ageRating
                )
                
                loadedContent.append(updatedContent)
            } catch let error as GoogleDriveService.DriveServiceError {
                print("📸 Error loading content for \(content.title): \(error.localizedDescription)")
                // Continue with other content even if one fails
                loadedContent.append(content)
            }
        }
        
        return loadedContent
    }
}

class HomeViewModel: ObservableObject {
    @Published var featuredContent: MediaContent?
    @Published var trendingContent: [MediaContent] = []
    @Published var continueWatchingContent: [MediaContent] = []
    @Published var myListContent: [MediaContent] = []
    @Published var films: [MediaContent] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    private let driveService = GoogleDriveService.shared
    private let contentLoader: ContentLoader
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        self.contentLoader = ContentLoader(driveService: driveService)
        loadContent()
    }
    
    func loadContent() {
        isLoading = true
        error = nil
        
        Task {
            do {
                let loadedContent = try await contentLoader.loadContent()
                await MainActor.run {
                    self.films = loadedContent
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.error = error
                    self.isLoading = false
                }
            }
        }
    }
    
    func filterContent(by tab: Int, genre: String?, searchText: String) -> [MediaContent] {
        var filtered = films
        
        // Filter by tab
        if tab == 0 {
            filtered = filtered.filter { $0.type == "FILM" }
        } else if tab == 1 {
            filtered = filtered.filter { $0.type == "SERIES" }
        }
        
        // Filter by genre
        if let genre = genre {
            filtered = filtered.filter { $0.genre == genre }
        }
        
        // Filter by search text
        if !searchText.isEmpty {
            filtered = filtered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
        }
        
        return filtered
    }
} 