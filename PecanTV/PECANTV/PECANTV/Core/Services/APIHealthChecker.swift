import Foundation
import SwiftUI

class APIHealthChecker: ObservableObject {
    @Published var isAPIAvailable: Bool = true
    @Published var isChecking: Bool = false
    
    static let shared = APIHealthChecker()
    
    private init() {}
    
    func checkAPIHealth(completion: ((Bool) -> Void)? = nil) {
        guard let url = URL(string: "http://localhost:8000/health") else {
            DispatchQueue.main.async {
                self.isAPIAvailable = false
                completion?(false)
            }
            return
        }
        
        isChecking = true
        var request = URLRequest(url: url)
        request.timeoutInterval = 3
        
        URLSession.shared.dataTask(with: request) { _, response, _ in
            DispatchQueue.main.async {
                self.isChecking = false
                if let httpResponse = response as? HTTPURLResponse {
                    self.isAPIAvailable = httpResponse.statusCode == 200
                } else {
                    self.isAPIAvailable = false
                }
                completion?(self.isAPIAvailable)
            }
        }.resume()
    }
    
    func showAPIErrorAlert() -> Alert {
        Alert(
            title: Text("Server Unavailable"),
            message: Text("The PecanTV server is currently unavailable. Please check your connection or try again later."),
            primaryButton: .default(Text("Retry")) {
                self.checkAPIHealth()
            },
            secondaryButton: .cancel()
        )
    }
    
    func retryConnection() {
        checkAPIHealth()
    }
} 