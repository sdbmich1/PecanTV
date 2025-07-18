import SwiftUI

struct MyPecanView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @EnvironmentObject private var favoritesManager: FavoritesManager
    @State private var showEditProfile = false
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var email = ""
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Custom Tab Picker
                HStack(spacing: 0) {
                    Button(action: { 
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedTab = 0 
                        }
                    }) {
                        VStack(spacing: 4) {
                            Text("Favorites")
                                .font(.headline)
                                .foregroundColor(selectedTab == 0 ? .pecanRed : .gray)
                            Rectangle()
                                .fill(selectedTab == 0 ? Color.pecanRed : Color.clear)
                                .frame(height: 2)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    
                    Button(action: { 
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedTab = 1 
                        }
                    }) {
                        VStack(spacing: 4) {
                            Text("Activity")
                                .font(.headline)
                                .foregroundColor(selectedTab == 1 ? .pecanRed : .gray)
                            Rectangle()
                                .fill(selectedTab == 1 ? Color.pecanRed : Color.clear)
                                .frame(height: 2)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    
                    Button(action: { 
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedTab = 2 
                        }
                    }) {
                        VStack(spacing: 4) {
                            Text("Account")
                                .font(.headline)
                                .foregroundColor(selectedTab == 2 ? .pecanRed : .gray)
                            Rectangle()
                                .fill(selectedTab == 2 ? Color.pecanRed : Color.clear)
                                .frame(height: 2)
                        }
                    }
                    .frame(maxWidth: .infinity)
                }
                .padding(.horizontal)
                .padding(.top, 8)
                
                // Content based on selected tab
                Group {
                    if selectedTab == 0 {
                        // Favorites Tab
                        FavoritesTabView()
                    } else if selectedTab == 1 {
                        // Activity Tab
                        ActivityTabView()
                    } else if selectedTab == 2 {
                        // Account Tab
                        AccountTabView(
                            showEditProfile: $showEditProfile,
                            firstName: $firstName,
                            lastName: $lastName,
                            email: $email
                        )
                    }
                }
                .transition(.opacity)
                .animation(.easeInOut(duration: 0.2), value: selectedTab)
            }
            .navigationTitle("My PECAN")
            .sheet(isPresented: $showEditProfile) {
                EditProfileSheet(
                    showEditProfile: $showEditProfile,
                    firstName: $firstName,
                    lastName: $lastName,
                    email: $email
                )
            }
        }
        .onAppear {
            // Ensure favorites are loaded when view appears
            favoritesManager.loadFavorites()
        }
    }
}

// MARK: - Favorites Tab View
struct FavoritesTabView: View {
    @EnvironmentObject private var favoritesManager: FavoritesManager
    
    var body: some View {
        ZStack {
            Color.white.edgesIgnoringSafeArea(.all)
            
            VStack(alignment: .leading, spacing: 0) {
                if favoritesManager.favoriteContent.isEmpty {
                    VStack(spacing: 16) {
                        Spacer()
                        Image(systemName: "heart.slash")
                            .font(.system(size: 48))
                            .foregroundColor(.gray)
                        Text("No Favorites Yet")
                            .font(.title2)
                            .fontWeight(.medium)
                            .foregroundColor(.black)
                        Text("Add movies and shows to your favorites to see them here")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                        Spacer()
                    }
                } else {
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 20) {
                            Text("My Favorites")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.black)
                                .padding(.horizontal)
                                .padding(.top, 20)
                            
                            FavoritesCarouselView(content: favoritesManager.favoriteContent)
                                .padding(.bottom, 100) // Space for tab bar
                        }
                    }
                }
            }
        }
        .onAppear {
            print("🔍 FavoritesTabView appeared with \(favoritesManager.favoriteContent.count) favorite items")
            print("🔍 Favorite IDs: \(favoritesManager.favoriteIds)")
            
            // Load favorites and ensure they're populated from available content
            favoritesManager.loadFavorites()
            
            // If we have favorite IDs but no content, try to populate from available content
            if !favoritesManager.favoriteIds.isEmpty && favoritesManager.favoriteContent.isEmpty {
                print("🔍 Attempting to populate favorites from available content in FavoritesTabView")
                // This will be handled by the FavoritesManager's loadFavorites method
            }
        }
    }
}

// MARK: - Activity Tab View
struct ActivityTabView: View {
    @State private var watchHistory: [WatchHistoryItem] = []
    @State private var notifications: [NotificationItem] = []
    @State private var isLoading = false
    
    var body: some View {
        ZStack {
            Color.white.edgesIgnoringSafeArea(.all)
            
            if isLoading {
                VStack {
                    ProgressView()
                        .scaleEffect(1.5)
                        .padding()
                    Text("Loading activity...")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
            } else {
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 24) {
                        // Watch History Section
                        VStack(alignment: .leading, spacing: 16) {
                            HStack {
                                Text("Watch History")
                                    .font(.title2)
                                    .fontWeight(.bold)
                                    .foregroundColor(.black)
                                
                                Spacer()
                                
                                Button("Clear All") {
                                    // Clear watch history
                                }
                                .font(.subheadline)
                                .foregroundColor(.pecanRed)
                            }
                            .padding(.horizontal)
                            
                            if watchHistory.isEmpty {
                                VStack(spacing: 12) {
                                    Image(systemName: "clock")
                                        .font(.system(size: 32))
                                        .foregroundColor(.gray)
                                    Text("No Watch History")
                                        .font(.headline)
                                        .foregroundColor(.black)
                                    Text("Your recently watched content will appear here")
                                        .font(.subheadline)
                                        .foregroundColor(.gray)
                                        .multilineTextAlignment(.center)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 40)
                            } else {
                                LazyVStack(spacing: 12) {
                                    ForEach(watchHistory) { item in
                                        WatchHistoryRow(item: item)
                                    }
                                }
                                .padding(.horizontal)
                            }
                        }
                        
                        // Notifications Section
                        VStack(alignment: .leading, spacing: 16) {
                            HStack {
                                Text("Notifications")
                                    .font(.title2)
                                    .fontWeight(.bold)
                                    .foregroundColor(.black)
                                
                                Spacer()
                                
                                Button("Mark All Read") {
                                    // Mark all notifications as read
                                }
                                .font(.subheadline)
                                .foregroundColor(.pecanRed)
                            }
                            .padding(.horizontal)
                            
                            if notifications.isEmpty {
                                VStack(spacing: 12) {
                                    Image(systemName: "bell.slash")
                                        .font(.system(size: 32))
                                        .foregroundColor(.gray)
                                    Text("No Notifications")
                                        .font(.headline)
                                        .foregroundColor(.black)
                                    Text("You're all caught up! New notifications will appear here")
                                        .font(.subheadline)
                                        .foregroundColor(.gray)
                                        .multilineTextAlignment(.center)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 40)
                            } else {
                                LazyVStack(spacing: 12) {
                                    ForEach(notifications) { notification in
                                        NotificationRow(notification: notification)
                                    }
                                }
                                .padding(.horizontal)
                            }
                        }
                    }
                    .padding(.top, 20)
                    .padding(.bottom, 100) // Space for tab bar
                }
            }
        }
        .onAppear {
            loadActivityData()
        }
    }
    
    private func loadActivityData() {
        isLoading = true
        
        // Simulate loading watch history and notifications
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.watchHistory = [
                WatchHistoryItem(
                    id: UUID(),
                    title: "The Count of Monte Cristo",
                    type: "SERIES",
                    posterURL: "https://storage.googleapis.com/pecantv_title_images/count_of_monte_cristo_poster.jpg",
                    watchedAt: Date().addingTimeInterval(-3600), // 1 hour ago
                    progress: 0.75
                ),
                WatchHistoryItem(
                    id: UUID(),
                    title: "Lady Frankenstein",
                    type: "FILM",
                    posterURL: "https://storage.googleapis.com/pecantv_title_images/lady_frankenstein_poster.jpg",
                    watchedAt: Date().addingTimeInterval(-7200), // 2 hours ago
                    progress: 1.0
                )
            ]
            
            self.notifications = [
                NotificationItem(
                    id: UUID(),
                    title: "New Episode Available",
                    message: "Episode 3 of 'The Count of Monte Cristo' is now available to watch",
                    type: .newContent,
                    timestamp: Date().addingTimeInterval(-1800), // 30 minutes ago
                    isRead: false
                ),
                NotificationItem(
                    id: UUID(),
                    title: "Welcome to PecanTV!",
                    message: "Thank you for joining PecanTV. Start exploring our collection of classic films and series.",
                    type: .welcome,
                    timestamp: Date().addingTimeInterval(-86400), // 1 day ago
                    isRead: true
                )
            ]
            
            self.isLoading = false
        }
    }
}

// MARK: - Watch History Item
struct WatchHistoryItem: Identifiable {
    let id: UUID
    let title: String
    let type: String
    let posterURL: String
    let watchedAt: Date
    let progress: Double // 0.0 to 1.0
}

// MARK: - Notification Item
struct NotificationItem: Identifiable {
    let id: UUID
    let title: String
    let message: String
    let type: NotificationType
    let timestamp: Date
    let isRead: Bool
}

enum NotificationType {
    case newContent
    case welcome
    case system
    case recommendation
}

// MARK: - Watch History Row
struct WatchHistoryRow: View {
    let item: WatchHistoryItem
    @State private var imageLoadError = false
    
    var body: some View {
        HStack(spacing: 12) {
            // Poster with better error handling
            Group {
                if imageLoadError {
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: 60, height: 90)
                        .cornerRadius(8)
                        .overlay(
                            Image(systemName: "photo")
                                .font(.title2)
                                .foregroundColor(.gray)
                        )
                } else {
                    AsyncImage(url: URL(string: item.posterURL)) { phase in
                        switch phase {
                        case .empty:
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(width: 60, height: 90)
                                .cornerRadius(8)
                                .overlay(
                                    ProgressView()
                                        .scaleEffect(0.8)
                                )
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(width: 60, height: 90)
                                .cornerRadius(8)
                        case .failure(_):
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(width: 60, height: 90)
                                .cornerRadius(8)
                                .overlay(
                                    Image(systemName: "photo")
                                        .font(.title2)
                                        .foregroundColor(.gray)
                                )
                        @unknown default:
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(width: 60, height: 90)
                                .cornerRadius(8)
                                .overlay(
                                    Image(systemName: "photo")
                                        .font(.title2)
                                        .foregroundColor(.gray)
                                )
                        }
                    }
                    .onAppear {
                        // Set a timeout for image loading
                        DispatchQueue.main.asyncAfter(deadline: .now() + 5.0) {
                            if !imageLoadError {
                                imageLoadError = true
                            }
                        }
                    }
                }
            }
            .frame(width: 60, height: 90)
            .cornerRadius(8)
            
            // Content info
            VStack(alignment: .leading, spacing: 4) {
                Text(item.title)
                    .font(.headline)
                    .foregroundColor(.black)
                    .lineLimit(2)
                
                Text(item.type)
                    .font(.caption)
                    .foregroundColor(.gray)
                
                Text(timeAgoString(from: item.watchedAt))
                    .font(.caption)
                    .foregroundColor(.gray)
                
                // Progress bar
                if item.progress < 1.0 {
                    ProgressView(value: item.progress)
                        .progressViewStyle(LinearProgressViewStyle(tint: .pecanRed))
                        .frame(height: 4)
                } else {
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.caption)
                            .foregroundColor(.green)
                        Text("Completed")
                            .font(.caption)
                            .foregroundColor(.green)
                    }
                }
            }
            
            Spacer()
            
            // Continue watching button
            if item.progress < 1.0 {
                Button("Continue") {
                    // Continue watching
                }
                .font(.caption)
                .foregroundColor(.pecanRed)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.pecanRed.opacity(0.1))
                .cornerRadius(12)
            }
        }
        .padding(.vertical, 8)
    }
    
    private func timeAgoString(from date: Date) -> String {
        let interval = Date().timeIntervalSince(date)
        if interval < 3600 {
            let minutes = Int(interval / 60)
            return "\(minutes) minute\(minutes == 1 ? "" : "s") ago"
        } else if interval < 86400 {
            let hours = Int(interval / 3600)
            return "\(hours) hour\(hours == 1 ? "" : "s") ago"
        } else {
            let days = Int(interval / 86400)
            return "\(days) day\(days == 1 ? "" : "s") ago"
        }
    }
}

// MARK: - Notification Row
struct NotificationRow: View {
    let notification: NotificationItem
    
    var body: some View {
        HStack(spacing: 12) {
            // Icon
            Image(systemName: iconForType(notification.type))
                .font(.title2)
                .foregroundColor(colorForType(notification.type))
                .frame(width: 40, height: 40)
                .background(colorForType(notification.type).opacity(0.1))
                .clipShape(Circle())
            
            // Content
            VStack(alignment: .leading, spacing: 4) {
                Text(notification.title)
                    .font(.headline)
                    .foregroundColor(.black)
                    .lineLimit(1)
                
                Text(notification.message)
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .lineLimit(2)
                
                Text(timeAgoString(from: notification.timestamp))
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            
            Spacer()
            
            // Unread indicator
            if !notification.isRead {
                Circle()
                    .fill(Color.pecanRed)
                    .frame(width: 8, height: 8)
            }
        }
        .padding(.vertical, 8)
        .opacity(notification.isRead ? 0.7 : 1.0)
    }
    
    private func iconForType(_ type: NotificationType) -> String {
        switch type {
        case .newContent:
            return "play.circle"
        case .welcome:
            return "hand.wave"
        case .system:
            return "gear"
        case .recommendation:
            return "star"
        }
    }
    
    private func colorForType(_ type: NotificationType) -> Color {
        switch type {
        case .newContent:
            return .blue
        case .welcome:
            return .green
        case .system:
            return .gray
        case .recommendation:
            return .orange
        }
    }
    
    private func timeAgoString(from date: Date) -> String {
        let interval = Date().timeIntervalSince(date)
        if interval < 3600 {
            let minutes = Int(interval / 60)
            return "\(minutes)m ago"
        } else if interval < 86400 {
            let hours = Int(interval / 3600)
            return "\(hours)h ago"
        } else {
            let days = Int(interval / 86400)
            return "\(days)d ago"
        }
    }
}

// MARK: - Account Tab View
struct AccountTabView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @Binding var showEditProfile: Bool
    @Binding var firstName: String
    @Binding var lastName: String
    @Binding var email: String
    
    var body: some View {
        List {
            Section(header: Text("Account")) {
                if let user = authViewModel.currentUser {
                    HStack {
                        Text("Name")
                        Spacer()
                        Text(user.fullName)
                            .foregroundColor(.gray)
                    }
                    
                    HStack {
                        Text("Email")
                        Spacer()
                        Text(user.email)
                            .foregroundColor(.gray)
                    }
                    
                    Button(action: {
                        // Load current user data
                        firstName = user.firstName
                        lastName = user.lastName
                        email = user.email
                        showEditProfile = true
                    }) {
                        Text("Edit Profile")
                            .foregroundColor(.blue)
                    }
                    
                    Button(action: {
                        authViewModel.signOut()
                    }) {
                        Text("Sign Out")
                            .foregroundColor(.pecanRed)
                    }
                }
            }
            
            // Removed empty Preferences section since all items were removed
            
            Section(header: Text("Support")) {
                NavigationLink(destination: HelpCenterView()) {
                    Label("Help Center", systemImage: "questionmark.circle")
                }
                
                NavigationLink(destination: ContactUsView()) {
                    Label("Contact Us", systemImage: "envelope")
                }
                
                NavigationLink(destination: Text("About")) {
                    Label("About", systemImage: "info.circle")
                }
            }
        }
    }
}

// MARK: - Edit Profile Sheet
struct EditProfileSheet: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @Binding var showEditProfile: Bool
    @Binding var firstName: String
    @Binding var lastName: String
    @Binding var email: String
    
    var body: some View {
        NavigationStack {
            Form {
                Section(header: Text("Personal Information")) {
                    HStack {
                        Text("First Name")
                            .frame(width: 100, alignment: .leading)
                        TextField("Enter first name", text: $firstName)
                    }
                    
                    HStack {
                        Text("Last Name")
                            .frame(width: 100, alignment: .leading)
                        TextField("Enter last name", text: $lastName)
                    }
                    
                    HStack {
                        Text("Email")
                            .frame(width: 100, alignment: .leading)
                        TextField("Email", text: $email)
                            .disabled(true) // Email can't be changed
                    }
                }
            }
            .navigationTitle("Edit Profile")
            .navigationBarItems(
                leading: Button("Cancel") {
                    showEditProfile = false
                },
                trailing: Button("Save") {
                    // Update local user data
                    if let user = authViewModel.currentUser {
                        authViewModel.currentUser = User(
                            id: user.id,
                            firstName: firstName,
                            lastName: lastName,
                            email: email
                        )
                    }
                    showEditProfile = false
                }
            )
        }
    }
}

#Preview {
    MyPecanView()
        .environmentObject(AuthViewModel())
        .environmentObject(FavoritesManager())
} 