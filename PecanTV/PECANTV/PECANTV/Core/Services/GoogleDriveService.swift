import Foundation

class GoogleDriveService: ObservableObject {
    static let shared = GoogleDriveService()
    
    @Published var files: [DriveFile] = []
    @Published var error: String?
    
    private init() {}
    
    enum DriveServiceError: Error {
        case fileNotFound(String)
        case invalidURL(String)
        case networkError(String)
        case invalidResponse(String)
    }
    
    func getTitleImageURL(for title: String) async throws -> URL {
        guard let url = GoogleDriveConfig.getTitleImageURL(for: title) else {
            throw DriveServiceError.invalidURL("Could not construct URL for \(title)")
        }
        return url
    }
    
    func getTrailerURL(for title: String) async throws -> URL {
        guard let url = GoogleDriveConfig.getTrailerURL(for: title) else {
            throw DriveServiceError.invalidURL("Could not construct URL for \(title)")
        }
        return url
    }
    
    func verifyTrailerURL(_ url: URL) async throws {
        print("🔍 Verifying trailer URL: \(url.absoluteString)")
        
        do {
            var request = URLRequest(url: url)
            request.httpMethod = "HEAD" // Use HEAD request for verification
            request.timeoutInterval = 10 // Shorter timeout for verification
            
            let (_, response) = try await URLSession.shared.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ Invalid response type for URL: \(url.absoluteString)")
                throw DriveServiceError.invalidResponse("Invalid response type")
            }
            
            print("📡 HTTP Status Code: \(httpResponse.statusCode) for URL: \(url.absoluteString)")
            
            guard httpResponse.statusCode == 200 else {
                print("❌ File not found (Status \(httpResponse.statusCode)) for URL: \(url.absoluteString)")
                throw DriveServiceError.fileNotFound("Status code: \(httpResponse.statusCode)")
            }
            
            print("✅ Successfully verified trailer URL: \(url.absoluteString)")
        } catch let error as DriveServiceError {
            print("❌ DriveServiceError: \(error)")
            throw error
        } catch {
            print("❌ Network error: \(error.localizedDescription)")
            throw DriveServiceError.networkError(error.localizedDescription)
        }
    }
    
    struct DriveFile: Identifiable, Codable {
        let id: String
        let name: String
        let mimeType: String
        let webViewLink: String
    }
} 