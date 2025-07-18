import Foundation
import SwiftUI
import UIKit // Added for UIDevice

class APIHealthChecker: ObservableObject {
    @Published var isAPIAvailable: Bool = true
    @Published var isChecking: Bool = false
    
    static let shared = APIHealthChecker()
    
    private init() {}
    
    func checkAPIHealth(completion: ((Bool) -> Void)? = nil) {
        print("🔍 APIHealthChecker: Starting health check...")
        
        guard let url = APIConfig.url(for: APIConfig.Endpoints.health) else {
            print("❌ APIHealthChecker: Invalid URL")
            DispatchQueue.main.async {
                self.isAPIAvailable = false
                completion?(false)
            }
            return
        }
        
        print("🔍 APIHealthChecker: Checking URL: \(url)")
        isChecking = true
        var request = URLRequest(url: url)
        request.timeoutInterval = 30  // Increased to 30 seconds for ngrok
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                self.isChecking = false
                
                if let error = error {
                    print("❌ APIHealthChecker: Network error: \(error.localizedDescription)")
                    self.isAPIAvailable = false
                    completion?(false)
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse {
                    print("📊 APIHealthChecker: HTTP Status: \(httpResponse.statusCode)")
                    
                    if httpResponse.statusCode == 200 {
                        print("✅ APIHealthChecker: API is available")
                        self.isAPIAvailable = true
                        completion?(true)
                    } else {
                        print("❌ APIHealthChecker: API returned status \(httpResponse.statusCode)")
                        self.isAPIAvailable = false
                        completion?(false)
                    }
                } else {
                    print("❌ APIHealthChecker: Invalid response")
                    self.isAPIAvailable = false
                    completion?(false)
                }
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