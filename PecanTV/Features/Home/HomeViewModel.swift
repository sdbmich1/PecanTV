import Foundation
import Combine

class HomeViewModel: ObservableObject {
    @Published var trendingContent: [Content] = []
    @Published var continueWatching: [Content] = []
    @Published var recommendedContent: [Content] = []
    @Published var error: String?
    
    private let contentService: ContentServiceProtocol
    private var cancellables = Set<AnyCancellable>()
    
    init(contentService: ContentServiceProtocol = ContentService()) {
        self.contentService = contentService
        loadContent()
    }
    
    func loadContent() {
        Publishers.Zip3(
            contentService.fetchTrending(),
            contentService.fetchContinueWatching(),
            contentService.fetchRecommended()
        )
        .receive(on: DispatchQueue.main)
        .sink { [weak self] completion in
            if case .failure(let error) = completion {
                self?.error = error.localizedDescription
            }
        } receiveValue: { [weak self] trending, continueWatching, recommended in
            self?.trendingContent = trending
            self?.continueWatching = continueWatching
            self?.recommendedContent = recommended
            self?.error = nil
        }
        .store(in: &cancellables)
    }
    
    func refresh() {
        loadContent()
    }
} 