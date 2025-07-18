import SwiftUI

struct HelpCenterView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var searchText = ""
    @State private var selectedCategory: HelpCategory?
    
    let helpCategories: [HelpCategory] = [
        HelpCategory(
            title: "Getting Started",
            icon: "play.circle.fill",
            articles: [
                HelpArticle(title: "How to watch content", content: "Browse our collection of classic films and TV series. Tap on any title to start watching immediately."),
                HelpArticle(title: "Creating your account", content: "Sign up with your email address to create your Pecan TV account and start enjoying classic entertainment."),
                HelpArticle(title: "Supported devices", content: "Pecan TV works on iOS devices running iOS 14.0 or later. We're working on expanding to other platforms.")
            ]
        ),
        HelpCategory(
            title: "Account & Billing",
            icon: "person.circle.fill",
            articles: [
                HelpArticle(title: "Managing your subscription", content: "Access your subscription details in the Profile section. You can update payment methods and view billing history."),
                HelpArticle(title: "Password reset", content: "If you've forgotten your password, use the 'Forgot Password' option on the sign-in screen."),
                HelpArticle(title: "Account settings", content: "Customize your viewing preferences, manage notifications, and control your privacy settings.")
            ]
        ),
        HelpCategory(
            title: "Troubleshooting",
            icon: "wrench.and.screwdriver.fill",
            articles: [
                HelpArticle(title: "Video won't play", content: "Check your internet connection. If the problem persists, try closing and reopening the app."),
                HelpArticle(title: "App crashes", content: "Update to the latest version of the app. If issues continue, try restarting your device."),
                HelpArticle(title: "Poor video quality", content: "Adjust streaming quality in Settings > Preferences > Streaming Quality based on your connection.")
            ]
        ),
        HelpCategory(
            title: "Content & Features",
            icon: "film.fill",
            articles: [
                HelpArticle(title: "Available content", content: "Pecan TV features classic films and TV series from the golden age of entertainment."),
                HelpArticle(title: "Adding to favorites", content: "Tap the heart icon on any title to add it to your favorites for easy access."),
                HelpArticle(title: "Search functionality", content: "Use the search bar to find specific titles, actors, or genres in our collection.")
            ]
        )
    ]
    
    var filteredCategories: [HelpCategory] {
        if searchText.isEmpty {
            return helpCategories
        } else {
            return helpCategories.compactMap { category in
                let filteredArticles = category.articles.filter { article in
                    article.title.localizedCaseInsensitiveContains(searchText) ||
                    article.content.localizedCaseInsensitiveContains(searchText)
                }
                return filteredArticles.isEmpty ? nil : HelpCategory(
                    title: category.title,
                    icon: category.icon,
                    articles: filteredArticles
                )
            }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Search Bar
                SearchBar(text: $searchText, placeholder: "Search help articles...")
                    .padding()
                
                if searchText.isEmpty {
                    // Categories View
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(filteredCategories, id: \.title) { category in
                                HelpCategoryCard(category: category) {
                                    selectedCategory = category
                                }
                            }
                            
                            // Contact Information Card
                            ContactInfoCard()
                        }
                        .padding()
                    }
                } else {
                    // Search Results
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(filteredCategories, id: \.title) { category in
                                VStack(alignment: .leading, spacing: 12) {
                                    Text(category.title)
                                        .font(.headline)
                                        .foregroundColor(.primary)
                                    
                                    ForEach(category.articles, id: \.title) { article in
                                        HelpArticleCard(article: article)
                                    }
                                }
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Help Center")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .sheet(item: $selectedCategory) { category in
                HelpCategoryDetailView(category: category)
            }
        }
    }
}

// MARK: - Supporting Views
struct HelpCategoryCard: View {
    let category: HelpCategory
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                Image(systemName: category.icon)
                    .font(.title2)
                    .foregroundColor(.pecanRed)
                    .frame(width: 32)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(category.title)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text("\(category.articles.count) articles")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct HelpArticleCard: View {
    let article: HelpArticle
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(article.title)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(.primary)
            
            Text(article.content)
                .font(.caption)
                .foregroundColor(.secondary)
                .lineLimit(3)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}

struct ContactInfoCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Still need help?")
                .font(.headline)
                .foregroundColor(.primary)
            
            VStack(alignment: .leading, spacing: 12) {
                ContactRow(
                    icon: "envelope.fill",
                    title: "Email Support",
                    subtitle: "help@pecantv.com",
                    action: {
                        if let url = URL(string: "mailto:help@pecantv.com") {
                            UIApplication.shared.open(url)
                        }
                    }
                )
                
                ContactRow(
                    icon: "phone.fill",
                    title: "Phone Support",
                    subtitle: "(415) 409-8863",
                    action: {
                        if let url = URL(string: "tel:4154098863") {
                            UIApplication.shared.open(url)
                        }
                    }
                )
                
                ContactRow(
                    icon: "location.fill",
                    title: "Mailing Address",
                    subtitle: "3450 Sacramento St., Ste 401\nSan Francisco, CA 94118",
                    action: {
                        if let url = URL(string: "https://maps.apple.com/?address=3450+Sacramento+St,+San+Francisco,+CA+94118") {
                            UIApplication.shared.open(url)
                        }
                    }
                )
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct ContactRow: View {
    let icon: String
    let title: String
    let subtitle: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .foregroundColor(.pecanRed)
                    .frame(width: 20)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.leading)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct HelpCategoryDetailView: View {
    let category: HelpCategory
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            List {
                ForEach(category.articles, id: \.title) { article in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(article.title)
                            .font(.headline)
                            .foregroundColor(.primary)
                        
                        Text(article.content)
                            .font(.body)
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 8)
                }
            }
            .navigationTitle(category.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Data Models
struct HelpCategory: Identifiable {
    let id = UUID()
    let title: String
    let icon: String
    let articles: [HelpArticle]
}

struct HelpArticle {
    let title: String
    let content: String
}

#Preview {
    HelpCenterView()
} 