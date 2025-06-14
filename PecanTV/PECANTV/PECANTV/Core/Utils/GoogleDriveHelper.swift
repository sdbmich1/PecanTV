import Foundation

class GoogleDriveHelper {
    static let shared = GoogleDriveHelper()
    
    // Base URL for Google Drive direct file access
    private let baseURL = "https://drive.google.com/uc?export=view&id="
    
    // File IDs for different types of content
    private let fileIDs: [String: String] = [
        // Posters
        "GetChristieLove": "YOUR_FILE_ID",
        "JesseOwens": "YOUR_FILE_ID",
        "MasterOfTheFlyingGuillotine": "YOUR_FILE_ID",
        "CarnivalOfSouls": "YOUR_FILE_ID",
        "JoeBullett": "YOUR_FILE_ID",
        "BlackBrigade": "YOUR_FILE_ID",
        "Dementia13": "YOUR_FILE_ID",
        "LittleShopOfHorrors": "YOUR_FILE_ID",
        "LastTimeISawParis": "YOUR_FILE_ID",
        "LoveAffair": "YOUR_FILE_ID",
        "ManWithTheGoldenArm": "YOUR_FILE_ID",
        
        // Trailers
        "GetChristieLoveTrailer": "YOUR_FILE_ID",
        "JesseOwensTrailer": "YOUR_FILE_ID",
        "JoeBullettTrailer": "YOUR_FILE_ID",
        "BlackBrigadeTrailer": "YOUR_FILE_ID",
        "NightOfTheLivingDeadTrailer": "YOUR_FILE_ID",
        
        // Content
        "GetChristieLoveContent": "YOUR_FILE_ID",
        "JesseOwensContent": "YOUR_FILE_ID",
        "JoeBullettContent": "YOUR_FILE_ID",
        "BlackBrigadeContent": "YOUR_FILE_ID",
        "NightOfTheLivingDeadContent": "YOUR_FILE_ID"
    ]
    
    private init() {}
    
    func getURL(for key: String) -> URL? {
        guard let fileID = fileIDs[key] else { return nil }
        return URL(string: baseURL + fileID)
    }
    
    func getPosterURL(for title: String) -> URL? {
        let key = title.replacingOccurrences(of: " ", with: "")
        return getURL(for: key)
    }
    
    func getTrailerURL(for title: String) -> URL? {
        let key = title.replacingOccurrences(of: " ", with: "") + "Trailer"
        return getURL(for: key)
    }
    
    func getContentURL(for title: String) -> URL? {
        let key = title.replacingOccurrences(of: " ", with: "") + "Content"
        return getURL(for: key)
    }
} 