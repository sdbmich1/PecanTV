import Foundation

struct GoogleDriveConfig {
    // Base URLs
    static let storageBaseURL = "https://storage.googleapis.com"
    static let titleImagesBucket = "pecantv_title_images"
    static let trailersBucket = "pecantv_trailers"
    
    // File naming patterns
    static let titleImagePattern = "{title}-Feature-Img-16x9.png"
    static let trailerPattern = "{title}_Trailer_35sFinal.mp4"
    
    // Error messages
    static let errorMessages: [String: String] = [
        "file_not_found": "File not found: {details}",
        "invalid_url": "Invalid URL: {details}",
        "network_error": "Network error: {details}",
        "invalid_response": "Invalid response: {details}"
    ]
    
    // Helper method to format titles for file names
    static func formatTitle(_ title: String) -> String {
        // Special case for "Black Brigade"
        if title == "Black Brigade" {
            return "BlackBrigade"
        }
        
        return title.replacingOccurrences(of: " ", with: "")
            .replacingOccurrences(of: "-", with: "")
    }
    
    // Get URL for title image
    static func getTitleImageURL(for title: String) -> URL? {
        let formattedTitle = formatTitle(title)
        let pattern = titleImagePattern.replacingOccurrences(of: "{title}", with: formattedTitle)
        return URL(string: "\(storageBaseURL)/\(titleImagesBucket)/\(pattern)")
    }
    
    // Get URL for trailer
    static func getTrailerURL(for title: String) -> URL? {
        let formattedTitle = formatTitle(title)
        let pattern = trailerPattern.replacingOccurrences(of: "{title}", with: formattedTitle)
        return URL(string: "\(storageBaseURL)/\(trailersBucket)/\(pattern)")
    }
} 