import Foundation
import Combine

class SearchViewModel: ObservableObject {
    @Published var searchResults: [Content] = []
    @Published var error: String?
    @Published var isLoading = false
    
    private let contentService: ContentServiceProtocol
    private var cancellables = Set<AnyCancellable>()
    private var searchSubject = PassthroughSubject<String, Never>()
    
    init(contentService: ContentServiceProtocol = ContentService()) {
        self.contentService = contentService
        
        // Debounce search requests
        searchSubject
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .sink { [weak self] query in
                self?.performSearch(query: query)
            }
            .store(in: &cancellables)
    }
    
    func search(query: String) {
        searchSubject.send(query)
    }
    
    private func performSearch(query: String) {
        guard !query.isEmpty else {
            searchResults = []
            return
        }
        
        isLoading = true
        
        contentService.search(query: query)
            .sink { [weak self] completion in
                self?.isLoading = false
                if case .failure(let error) = completion {
                    self?.error = error.localizedDescription
                }
            } receiveValue: { [weak self] results in
                self?.searchResults = results
                self?.error = nil
            }
            .store(in: &cancellables)
    }
} 