import Foundation
import SwiftUI

class APIHealthChecker: ObservableObject {
    @Published var isAPIAvailable: Bool = true
    @Published var isChecking: Bool = false
    
    static let shared = APIHealthChecker()
    
    private init() {}
    
    func checkAPIHealth(completion: ((Bool) -> Void)? = nil) {
        guard let url = URL(string: "https://77b9-192-69-240-171.ngrok-free.app/health") else {
            DispatchQueue.main.async {
                self.isAPIAvailable = false
                completion?(false)
            }
            return
        }
        
        isChecking = true
        var request = URLRequest(url: url)
        request.timeoutInterval = 10  // Increased from 3 to 10 seconds
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                self.isChecking = false
                
                if let error = error {
                    print("⚠️ API Health check error: \(error.localizedDescription)")
                    self.isAPIAvailable = false
                    completion?(false)
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse {
                    self.isAPIAvailable = httpResponse.statusCode == 200
                    if self.isAPIAvailable {
                        print("✅ API Health check successful")
                    } else {
                        print("❌ API Health check failed with status: \(httpResponse.statusCode)")
                    }
                } else {
                    self.isAPIAvailable = false
                    print("❌ API Health check failed - no response")
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