import Foundation
import Combine

protocol ContentServiceProtocol {
    func fetchTrending() -> AnyPublisher<[Content], Error>
    func fetchContinueWatching() -> AnyPublisher<[Content], Error>
    func fetchRecommended() -> AnyPublisher<[Content], Error>
    func fetchContent(id: String) -> AnyPublisher<Content, Error>
    func search(query: String) -> AnyPublisher<[Content], Error>
    func fetchByGenre(_ genre: String) -> AnyPublisher<[Content], Error>
}

class ContentService: ContentServiceProtocol {
    private let networkManager: NetworkManager
    
    init(networkManager: NetworkManager = .shared) {
        self.networkManager = networkManager
    }
    
    func fetchTrending() -> AnyPublisher<[Content], Error> {
        return networkManager.request(Config.Endpoints.trending())
    }
    
    func fetchContinueWatching() -> AnyPublisher<[Content], Error> {
        return networkManager.request(Config.Endpoints.continueWatching())
    }
    
    func fetchRecommended() -> AnyPublisher<[Content], Error> {
        return networkManager.request(Config.Endpoints.recommended())
    }
    
    func fetchContent(id: String) -> AnyPublisher<Content, Error> {
        return networkManager.request(Config.Endpoints.content(id: id))
    }
    
    func search(query: String) -> AnyPublisher<[Content], Error> {
        return networkManager.request(Config.Endpoints.search(query: query))
    }
    
    func fetchByGenre(_ genre: String) -> AnyPublisher<[Content], Error> {
        return networkManager.request(Config.Endpoints.genre(genre))
    }
} 