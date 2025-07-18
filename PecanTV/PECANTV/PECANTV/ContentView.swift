//
//  ContentView.swift
//  PECANTV
//
//  Created by Sean Brown on 5/20/25.
//

import SwiftUI
// import FirebaseCore
// import FirebaseAuth

struct ContentView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @EnvironmentObject private var contentViewModel: ContentViewModel
    @StateObject private var favoritesManager = FavoritesManager.shared
    @StateObject private var healthChecker = APIHealthChecker.shared
    @State private var selectedTab = 0
    @State private var showAPIErrorAlert = false
    @State private var hasInitialized = false
    
    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                TabView(selection: $selectedTab) {
                    // Use LazyView for better performance - only load when tab is selected
                    LazyView {
                        HomeView()
                    }
                    .tabItem {
                        Label("Home", systemImage: "house")
                    }
                    .tag(0)
                    
                    LazyView {
                        FavoritesView(allContent: contentViewModel.films + contentViewModel.tvSeries)
                            .environmentObject(favoritesManager)
                            .onAppear {
                                print("🔍 Favorites tab appeared")
                                favoritesManager.loadFavorites()
                            }
                    }
                    .tabItem {
                        Label("My Favs", systemImage: "heart")
                    }
                    .tag(1)
                    
                    LazyView {
                        MyPecanView()
                            .environmentObject(favoritesManager)
                            .onAppear {
                                print("🔍 MyPecan tab appeared")
                                favoritesManager.loadFavorites()
                            }
                    }
                    .tabItem {
                        Label("My PECAN", systemImage: "person")
                    }
                    .tag(2)
                }
                .onAppear {
                    // Preload content when main tab view appears
                    if !hasInitialized {
                        hasInitialized = true
                        print("📱 ContentView: Main tab view appeared, initializing...")
                        
                        // Preload essential content in background
                        Task {
                            await preloadEssentialContent()
                        }
                    }
                }
            } else if !healthChecker.isAPIAvailable {
                VStack(spacing: 20) {
                    Image(systemName: "wifi.slash")
                        .font(.system(size: 60))
                        .foregroundColor(.red)
                    
                    Text("Server Unavailable")
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Text("Unable to connect to PecanTV server. Please check your connection and try again.")
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                        .padding(.horizontal)
                    
                    Button("Retry Connection") {
                        healthChecker.checkAPIHealth()
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            } else {
                SignInView()
                    .environmentObject(authViewModel)
            }
        }
        .onAppear {
            print("🏠 ContentView appeared")
            
            // Always set up authentication success callback
            authViewModel.onAuthenticationSuccess = {
                print("🎉 Authentication successful, loading content...")
                contentViewModel.loadContent()
            }
            
            // If user is already authenticated and API is available, load content
            if authViewModel.isAuthenticated && healthChecker.isAPIAvailable && contentViewModel.films.isEmpty && contentViewModel.tvSeries.isEmpty {
                print("🔄 ContentView: User authenticated and API available, loading content")
                contentViewModel.loadContent()
            }
        }
        .onChange(of: healthChecker.isAPIAvailable) { oldValue, newValue in
            print("🔄 API availability changed: \(oldValue) -> \(newValue)")
            if newValue && authViewModel.isAuthenticated {
                print("🔄 API became available and user is authenticated, loading content...")
                contentViewModel.loadContent()
            }
            if !newValue {
                showAPIErrorAlert = true
            }
        }
        .onChange(of: authViewModel.isAuthenticated) { oldValue, newValue in
            print("🔄 Authentication state changed: \(oldValue) -> \(newValue)")
            if newValue && healthChecker.isAPIAvailable {
                print("🔄 User became authenticated and API is available, loading content...")
                contentViewModel.loadContent()
            }
        }
        .alert("Server Unavailable", isPresented: $showAPIErrorAlert) {
            Button("Retry") {
                healthChecker.checkAPIHealth()
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("The PecanTV server is currently unavailable. Please check your connection or try again later.")
        }
    }
    
    /// Preload essential content in background for better performance
    private func preloadEssentialContent() async {
        print("🚀 ContentView: Preloading essential content...")
        
        // Preload first few images from content
        let allContent = contentViewModel.films + contentViewModel.tvSeries
        let firstFewContent = Array(allContent.prefix(6))
        let imageURLs = firstFewContent.compactMap { content -> String? in
            guard !content.posterURL.isEmpty else { return nil }
            return content.posterURL
        }
        
        // Safety check - only preload if we have valid URLs
        guard !imageURLs.isEmpty else {
            print("⚠️ No valid image URLs to preload")
            return
        }
        
        print("📸 Preloading \(imageURLs.count) images: \(imageURLs)")
        
        // Preload images in background
        SimpleImageService.shared.preloadImages(imageURLs)
        
        print("✅ ContentView: Essential content preloading initiated")
    }
}

// MARK: - Lazy View for Performance

struct LazyView<Content: View>: View {
    let build: () -> Content
    @State private var isLoaded = false
    
    init(_ build: @escaping () -> Content) {
        self.build = build
    }
    
    var body: some View {
        Group {
            if isLoaded {
                build()
            } else {
                Color.clear
                    .onAppear {
                        isLoaded = true
                    }
            }
        }
    }
}

#Preview {
    ContentView()
}
