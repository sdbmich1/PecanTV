import Foundation
import FirebaseFirestore

class ContentViewModel: ObservableObject {
    @Published var films: [MediaContent] = []
    @Published var tvSeries: [MediaContent] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    private let db = Firestore.firestore()
    
    init() {
        fetchContent()
    }
    
    func fetchContent() {
        isLoading = true
        
        db.collection("films").getDocuments { [weak self] snapshot, error in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                if let error = error {
                    self?.error = error
                    return
                }
                
                guard let documents = snapshot?.documents else {
                    self?.error = NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "No films found"])
                    return
                }
                
                self?.films = documents.compactMap { document in
                    let data = document.data()
                    return MediaContent(
                        id: Int(document.documentID) ?? 0,
                        title: data["title"] as? String ?? "",
                        posterURL: data["posterURL"] as? String ?? "",
                        trailerURL: data["trailerURL"] as? String ?? "",
                        contentURL: data["contentURL"] as? String ?? "",
                        description: data["description"] as? String ?? "",
                        type: data["type"] as? String ?? "FILM",
                        runtime: data["runtime"] as? Int ?? 0,
                        genre: data["genre"] as? String ?? "",
                        ageRating: data["ageRating"] as? String ?? ""
                    )
                }
            }
        }
    }
    
    func getContentsByGenre(_ genre: String) -> [MediaContent] {
        return films.filter { $0.genre.contains(genre) }
    }
} 