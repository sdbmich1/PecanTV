import Foundation

extension String {
    /// Truncates the string to the specified length and adds ellipsis if needed
    /// - Parameter maxLength: Maximum length before truncation (default: 30)
    /// - Returns: Truncated string with ellipsis if needed
    func truncatedTitle(maxLength: Int = 30) -> String {
        if self.count <= maxLength {
            return self
        }
        
        let truncated = String(self.prefix(maxLength - 3))
        return truncated + "..."
    }
    
    /// Truncates the string to the specified length and adds ellipsis if needed
    /// This version preserves word boundaries when possible
    /// - Parameter maxLength: Maximum length before truncation (default: 30)
    /// - Returns: Truncated string with ellipsis if needed
    func truncatedTitleWithWordBoundary(maxLength: Int = 30) -> String {
        if self.count <= maxLength {
            return self
        }
        
        let words = self.components(separatedBy: " ")
        var result = ""
        
        for word in words {
            let testResult = result.isEmpty ? word : result + " " + word
            if testResult.count <= maxLength - 3 {
                result = testResult
            } else {
                break
            }
        }
        
        if result.isEmpty {
            // If no words fit, just truncate at character level
            return String(self.prefix(maxLength - 3)) + "..."
        }
        
        return result + "..."
    }
} 