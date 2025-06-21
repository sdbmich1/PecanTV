import SwiftUI

extension Color {
    // Brand Colors
    static let pecanRed = Color(red: 239/255, green: 74/255, blue: 35/255) // EF4A23
    
    // Semantic Colors
    static let pecanPrimary = pecanRed
    static let pecanSecondary = Color(red: 45/255, green: 45/255, blue: 45/255) // Dark gray
    static let pecanBackground = Color.black
    static let pecanSurface = Color(red: 20/255, green: 20/255, blue: 20/255) // Very dark gray
    
    // Text Colors
    static let pecanTextPrimary = Color.white
    static let pecanTextSecondary = Color.gray
    static let pecanTextMuted = Color(red: 120/255, green: 120/255, blue: 120/255)
    
    // Status Colors
    static let pecanSuccess = Color.green
    static let pecanWarning = Color.orange
    static let pecanError = pecanRed
    static let pecanInfo = Color.blue
} 