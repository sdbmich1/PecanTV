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
    @StateObject private var authViewModel = AuthViewModel()
    @StateObject private var contentViewModel = ContentViewModel()
    @StateObject private var favoritesManager = FavoritesManager()
    @StateObject private var healthChecker = APIHealthChecker.shared
    @State private var selectedTab = 0
    @State private var showAPIErrorAlert = false
    
    var body: some View {
        Group {
            if healthChecker.isChecking {
                VStack {
                    ProgressView("Checking server status...")
                        .padding()
                    Text("Please wait while we connect to PecanTV")
                        .foregroundColor(.secondary)
                }
            } else if !healthChecker.isAPIAvailable {
                VStack(spacing: 20) {
                    Image(systemName: "wifi.slash")
                        .font(.system(size: 60))
                        .foregroundColor(.red)
                    
                    Text("Server Unavailable")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("The PecanTV server is currently unavailable.\nPlease check your connection or try again later.")
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
                TabView(selection: $selectedTab) {
                    HomeView()
                        .environmentObject(contentViewModel)
                        .environmentObject(favoritesManager)
                        .environmentObject(healthChecker)
                        .tabItem {
                            Label("Home", systemImage: "house")
                        }
                        .tag(0)
                    
                    FavoritesView(allContent: contentViewModel.films + contentViewModel.tvSeries)
                        .environmentObject(favoritesManager)
                        .environmentObject(healthChecker)
                        .tabItem {
                            Label("My Favs", systemImage: "heart")
                        }
                        .tag(1)
                    
                    ProfileView()
                        .environmentObject(favoritesManager)
                        .environmentObject(healthChecker)
                        .tabItem {
                            Label("My PECAN", systemImage: "person")
                        }
                        .tag(2)
                }
            }
        }
        .onAppear {
            // Check API health on app launch
            healthChecker.checkAPIHealth { isAvailable in
                if isAvailable {
                    // Set up authentication success callback
                    authViewModel.onAuthenticationSuccess = {
                        print("🎉 Authentication successful, loading content...")
                        contentViewModel.loadContent()
                    }
                }
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
}

#Preview {
    ContentView()
}
